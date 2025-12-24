from odoo import models, fields, api
import xmlrpc.client


class RpcSettings(models.Model):
    _name = 'rpc.settings'
    _description = "Paramètres RPC"

    # Source
    source_host = fields.Char("Hôte source", required=True)
    source_port = fields.Char("Port source", default='8069', required=True)
    source_db = fields.Char("Base source", required=True)
    source_user = fields.Char("Utilisateur source", required=True)
    source_password = fields.Char("Mot de passe source", required=True)

    # Destination
    dest_host = fields.Char("Hôte destination", required=True)
    dest_port = fields.Char("Port destination", default='8069', required=True)
    dest_db = fields.Char("Base destination", required=True)
    dest_user = fields.Char("Utilisateur destination", required=True)
    dest_password = fields.Char("Mot de passe destination", required=True)

    last_transfer_date = fields.Datetime("Dernier transfert")

    def action_run_rpc_transfer(self):
        """Lancer le transfert RPC selon les paramètres configurés"""
        for rec in self:
            try:
                url_src = f"http://{rec.source_host}:{rec.source_port}"

                common_src = xmlrpc.client.ServerProxy(f"{url_src}/xmlrpc/2/common")
                uid_src = common_src.authenticate(rec.source_db, rec.source_user, rec.source_password, {})
                if not uid_src:
                    raise ValueError("Échec d'authentification sur la base source")

                models_src = xmlrpc.client.ServerProxy(f"{url_src}/xmlrpc/2/object")

                # Récupérer les produits source
                source_products = models_src.execute_kw(
                    rec.source_db, uid_src, rec.source_password,
                    'product.template', 'search_read',
                    [[]], {'fields': ['name', 'image_1920']}
                )

                # Connexion destination
                url_dest = f"http://{rec.dest_host}:{rec.dest_port}"
                common_dest = xmlrpc.client.ServerProxy(f"{url_dest}/xmlrpc/2/common")
                uid_dest = common_dest.authenticate(rec.dest_db, rec.dest_user, rec.dest_password, {})
                if not uid_dest:
                    raise ValueError("Échec d'authentification sur la base destination")

                models_dest = xmlrpc.client.ServerProxy(f"{url_dest}/xmlrpc/2/object")

                # Produits destination
                dest_products = models_dest.execute_kw(
                    rec.dest_db, uid_dest, rec.dest_password,
                    'product.template', 'search_read',
                    [[]], {'fields': ['name']}
                )

                dest_dict = {p['name']: p['id'] for p in dest_products}

                count = 0
                for src in source_products:
                    dest_id = dest_dict.get(src['name'])
                    if dest_id and src.get('image_1920'):
                        models_dest.execute_kw(
                            rec.dest_db, uid_dest, rec.dest_password,
                            'product.template', 'write',
                            [[dest_id], {'image_1920': src['image_1920']}]
                        )
                        count += 1

                rec.last_transfer_date = fields.Datetime.now()

                # Notification succès
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': "Transfert terminé",
                        'message': f"{count} images transférées avec succès.",
                        'sticky': False,
                        'type': 'success',
                    }
                }

            except Exception as e:
                # Notification erreur
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': "Erreur RPC",
                        'message': str(e),
                        'sticky': True,
                        'type': 'danger',
                    }
                }

