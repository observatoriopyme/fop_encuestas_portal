from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EncuestasPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'encuestas_count' in counters:
            values['encuestas_count'] = len(self._get_user_encuestas())
        return values

    def _get_encuestas_folder(self):
        return request.env['documents.folder'].sudo().search(
            [('name', '=', 'Encuestas')], limit=1
        )

    def _get_user_encuestas(self):
        user_login = request.env.user.login
        folder = self._get_encuestas_folder()
        if not folder:
            return request.env['documents.document'].sudo().browse()
        return request.env['documents.document'].sudo().search([
            ('folder_id', '=', folder.id),
            ('name', '=ilike', f'{user_login}@%.pdf'),
        ])

    def _parse_survey_id(self, doc_name, user_login):
        """Extract survey ID from document name: [login]@[survey_id].pdf"""
        prefix = f'{user_login}@'
        name = doc_name[len(prefix):] if doc_name.lower().startswith(prefix.lower()) else doc_name
        return name[:-4] if name.lower().endswith('.pdf') else name

    @http.route(['/my/encuestas'], type='http', auth='user', website=True)
    def portal_my_encuestas(self, **kw):
        values = self._prepare_portal_layout_values()
        encuestas = self._get_user_encuestas()
        user_login = request.env.user.login
        encuestas_data = []
        for doc in encuestas:
            survey_id = self._parse_survey_id(doc.name, user_login)
            encuestas_data.append({
                'doc': doc,
                'survey_id': survey_id,
                'date': doc.write_date.strftime('%d/%m/%Y') if doc.write_date else '',
            })
        values.update({
            'encuestas_data': encuestas_data,
            'page_name': 'encuestas',
        })
        return request.render('fop_encuestas_portal.portal_my_encuestas', values)

    @http.route(['/my/encuestas/<string:survey_id>.pdf'], type='http', auth='user', website=True)
    def portal_my_encuesta_pdf(self, survey_id, **kw):
        user_login = request.env.user.login
        folder = self._get_encuestas_folder()
        if not folder:
            return request.not_found()

        doc_name = f'{user_login}@{survey_id}.pdf'
        document = request.env['documents.document'].sudo().search([
            ('folder_id', '=', folder.id),
            ('name', '=ilike', doc_name),
        ], limit=1)

        if not document:
            return request.not_found()

        return request.env['ir.binary']._get_stream_from(
            document, field_name='raw', filename=document.name
        ).get_response(as_attachment=False)
