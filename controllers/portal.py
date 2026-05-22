from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class EncuestasPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'surveys_count' in counters:
            values['surveys_count'] = len(self._get_user_surveys())
        return values

    def _get_surveys_folder(self):
        Folder = request.env['documents.folder'].sudo()
        for lang, name in (('es_AR', 'Encuestas'), ('en_US', 'Surveys')):
            folder = Folder.with_context(lang=lang).search([('name', '=ilike', name)], limit=1)
            if folder:
                return folder
        return Folder.browse()

    def _get_user_surveys(self):
        folder = self._get_surveys_folder()
        if not folder:
            return request.env['documents.document'].browse()
        return request.env['documents.document'].search([
            ('folder_id', '=', folder.id),
        ])

    @http.route(['/my/encuestas'], type='http', auth='user', website=True)
    def portal_my_encuestas(self, **kw):
        values = self._prepare_portal_layout_values()
        surveys = self._get_user_surveys()
        survey_documents_data = []
        for i, doc in enumerate(surveys, start=1):
            token = doc.sudo().attachment_id.generate_access_token()[0]
            survey_documents_data.append({
                'label': f'Encuesta #{i}',
                'date': doc.write_date.strftime('%d/%m/%Y') if doc.write_date else '',
                'url': f'/my/encuestas/{token}',
            })
        values.update({
            'surveys_data': survey_documents_data,
            'page_name': 'surveys',
        })
        return request.render('fop_encuestas_portal.portal_my_surveys_list', values)

    @http.route(['/my/encuestas/<string:access_token>'], type='http', auth='user', website=True)
    def portal_my_survey_pdf(self, access_token):
        document = request.env['documents.document'].sudo().search([
            ('attachment_id.access_token', '=', access_token),
        ], limit=1)

        if not document:
            return request.not_found()

        return request.env['ir.binary']._get_stream_from(
            document, field_name='raw', filename=document.name
        ).get_response(as_attachment=False)

