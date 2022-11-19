from apps.alerts.incident_appearance.templaters.alert_templater import AlertTemplater


# This will be the location for customizing any rendering, by overriding methods from the base class
class AlertMatrixTemplater(AlertTemplater):
    RENDER_FOR_MATRIX = "matrix"

    def _render_for(self):
        return self.RENDER_FOR_MATRIX


def build_message(alert_group, user_id):
    alert = alert_group.alerts.first()
    templated_alert = AlertMatrixTemplater(alert).render()
    return f"{user_id} {templated_alert.message}"
    # Email Templater then calls `convert_md_to_html` and `render_to_string`
    # but I _suspect_ we won't need that as Matrix accepts raw Markdown

