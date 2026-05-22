import os
import sys
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import toml
from csscompressor import compress as css_compress
from jsmin import jsmin

try:
    import htmlmin
except Exception:
    htmlmin = None

from paths import BASE_DIR, CONTENT_FOLDER

class TagGenerator:
    """Classe pour generer dynamiquement les elements HTML a partir de donnees TOML d'incidents"""
    def __init__(self, html_file, toml_folder):
        """Initialise avec le fichier HTML template et le dossier contenant les TOML"""
        self.html_file = html_file
        self.toml_folder = toml_folder
        self.data = None  # Stocker les donnees TOML actuelles
        self.infos = None  # Stocker les informations du rapport

        self.base_dir = BASE_DIR
        self.folder = CONTENT_FOLDER
        self.toml_files = []
        try:
            self.toml_files = [
                name for name in os.listdir(self.folder)
                if os.path.isfile(os.path.join(self.folder, name))
            ]
        except FileNotFoundError:
            print("no content folder found")
        
        # Parse le fichier HTML template avec BeautifulSoup
        try:
            with open(self.html_file, 'r', encoding='utf-8') as file:
                self.soup = BeautifulSoup(file, 'html.parser')
        except Exception as e:
            print("no html file given", e)

    def add_section(self, product_id, css_class, parent_tag = "main .card-container", attributes=None):
        """Ajoute une nouvelle section (div) au DOM avec un ID et des attributs specifiques"""
        parent = self.soup.select_one(parent_tag)

        if not parent:
            raise ValueError(f"Parent element '{parent_tag}' not found")
        
        section = self.soup.new_tag('section')
        section['id'] = product_id
        section['class'] = css_class
        section['href'] = f"#{product_id}"
        section['data-product-id'] = product_id

        if attributes:
            for key, value in attributes.items():
                section[key] = value

        parent.append(section)
        return section
        
    
    def add_tag(self, tag_name, parent_selector='body', content='', attributes=None, position='append'):
        """Ajoute un element HTML avec contenu et attributs optionnels au parent specifie"""
        parent = self.soup.select_one(parent_selector)

        if not parent:
            raise ValueError(f"Parent element '{parent_selector}' not found")
        
        new_tag = self.soup.new_tag(tag_name)
        
        if content:
            new_tag.string = content

        if attributes:
            for key, value in attributes.items():
                new_tag[key] = value
        
        # Positionne l'element au sein du parent (append, prepend, ou before)
        if position == 'append':
            parent.append(new_tag)
        elif position == 'prepend':
            parent.insert(0, new_tag)
        elif position == 'before':
            parent.insert_before(new_tag)
        
        return new_tag
    
    def generate_nav_items(self, files):
        nav_items = []

        radio_options = [
            ("sort-new-to-old-btn", "Sort by Newest"),
            ("sort-old-to-new-btn", "Sort by Oldest"),
            ("sort-alphabetically-btn", "Sort Alphabetically"),
            ("sort-severity-btn", "Sort by Severity"),
        ]

        for idx, (radio_id, label_text) in enumerate(radio_options):
            self.add_tag('div', parent_selector='nav .nav-menu .search-container', attributes={'class': 'sort-option'})
            input_attributes = {'id': radio_id, 'type': 'radio', 'name': 'sort', 'value': radio_id}
            if idx == 0:
                input_attributes['checked'] = 'checked'

            self.add_tag('input', parent_selector='nav .nav-menu .search-container .sort-option:last-child', attributes=input_attributes)
            self.add_tag('label', parent_selector='nav .nav-menu .search-container .sort-option:last-child', content=label_text, attributes={'for': radio_id})

        for file in files:
            file_id = os.path.splitext(os.path.basename(file))[0]

            created_at = None
            with open(os.path.join(CONTENT_FOLDER, file), 'r', encoding='utf-8') as f:
                data = toml.load(f)
                created_at = data.get('report', {}).get('created_at')

            section_id = f"incident-{file_id}"
            self.add_tag('li', parent_selector='nav ul', attributes={'data-time': created_at, 'class': 'nav-item', 'data-time-ts': str(int(datetime.fromisoformat(created_at).timestamp()))})
            self.add_tag('a', parent_selector='nav ul li:last-child', content=file_id, attributes={'href': f"#{section_id}"})
        return nav_items
    
    def generate_card_info(self, toml_file):
        """Generation des carte affichées sur la page d'accueil, avec les informations de base du rapport d'incident"""
        file_name = os.path.basename(toml_file)
        file_id = os.path.splitext(file_name)[0]
        section_id = f"incident-{file_id}"
        section_selector = f"#{section_id}"

        print(f"Generating HTML for TOML file: {toml_file}, section ID: {section_id}")
        
        try:
            toml_path = os.path.join(CONTENT_FOLDER, toml_file)
            with open(toml_path, 'r', encoding='utf-8') as f:
                self.infos = toml.load(f)
        except Exception as e:
            print(f"Error loading TOML file: {toml_file}", e)
            return False


        
        created_at = self.infos.get('report', {}).get('created_at')
        section_attributes = {}

        if created_at:
            section_attributes['data-time'] = created_at
            section_attributes['data-time-ts'] = str(int(datetime.fromisoformat(created_at).timestamp()))

        
        
        try:
            self.add_section(section_id, "incident-section", attributes=section_attributes)
        except Exception as e:
            print(f"Error adding section for file: {toml_file}", e)
            return False
        
        report_id = f"report-{file_id}"
        report_selector = f"#{report_id}"
        self.add_tag('div', parent_selector=section_selector,
                                   attributes={'class': 'incident-report', 'id': report_id})
        
        if 'report' in self.infos:
            report = self.infos['report']
            
            self.add_tag('header', parent_selector=report_selector,
                                      attributes={'class': 'report-header'})
            
            self.add_tag('h1', parent_selector=f"{report_selector} .report-header",
                                      content=report.get('title', 'Incident Report'),
                                      attributes={'class': 'report-title'})
            
            self.add_tag('div', parent_selector=f"{report_selector} .report-header",
                                      attributes={'class': 'meta-info'})
            
            self.add_tag('span', parent_selector=f"{report_selector} .meta-info",
                                      content=f"Ticket: {report.get('ticket_id', 'N/A')}",
                                      attributes={'class': 'ticket-id'})
            
            self.add_tag('span', parent_selector=f"{report_selector} .meta-info",
                                      content=f"Status: {report.get('status', 'Unknown')}",
                                      attributes={'class': f"status status-{report.get('status', '').lower()}"})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Priority: {report.get('priority', 'N/A')}",
                                      attributes={'class': 'report-priority'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Severity: {report.get('severity', 'N/A')}",
                                      attributes={'class': 'report-severity', 'data-severity': report.get('severity', 'N/A').lower()})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Category: {report.get('category', 'N/A')}",
                                      attributes={'class': 'report-category'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Created At: {report.get('created_at', 'N/A')}",
                                      attributes={'class': 'report-created-at'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Resolved At: {report.get('resolved_at', 'N/A')}",
                                      attributes={'class': 'report-resolved-at'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Report Author: {report.get('report_author', 'N/A')}",
                                      attributes={'class': 'report-author'})     
            self.add_tag('button', parent_selector=report_selector,
                                      content='Show Details',
                                      attributes={'class': 'toggle-details-btn', 'data-target': f"#{section_id}-hidden"})   

    def generate_html_from_toml(self, toml_file):
        """Genere les details complets du rapport d'incident (cache) a partir d'un fichier TOML"""
        file_name = os.path.basename(toml_file)
        file_id = os.path.splitext(file_name)[0]
        section_id = f"incident-{file_id}-hidden"
        section_selector = f"#{section_id}"

        print(f"Generating HTML for TOML file: {toml_file}, section ID: {section_id}")
        
        try:
            toml_path = os.path.join(CONTENT_FOLDER, toml_file)
            with open(toml_path, 'r', encoding='utf-8') as f:
                self.data = toml.load(f)
        except Exception as e:
            print(f"Error loading TOML file: {toml_file}", e)
            return False
    
        section_attributes = {}
        section_attributes['hidden'] = 'true'
        
        try:
            self.add_section(section_id, "incident-section-hidden", attributes=section_attributes)
        except Exception as e:
            print(f"Error adding section for file: {toml_file}", e)
            return False
        
        report_id = f"report-{file_id}-hidden"
        report_selector = f"#{report_id}"
        self.add_tag('div', parent_selector=section_selector,
                                   attributes={'class': 'incident-report', 'id': report_id})
        
        if 'report' in self.data:
            report = self.data['report']
            
            self.add_tag('header', parent_selector=report_selector,
                                      attributes={'class': 'report-header'})
            
            self.add_tag('h1', parent_selector=f"{report_selector} .report-header",
                                      content=report.get('title', 'Incident Report'),
                                      attributes={'class': 'report-title'})
            
            self.add_tag('div', parent_selector=f"{report_selector} .report-header",
                                      attributes={'class': 'meta-info'})
            
            self.add_tag('span', parent_selector=f"{report_selector} .meta-info",
                                      content=f"Ticket: {report.get('ticket_id', 'N/A')}",
                                      attributes={'class': 'ticket-id'})
            
            self.add_tag('span', parent_selector=f"{report_selector} .meta-info",
                                      content=f"Status: {report.get('status', 'Unknown')}",
                                      attributes={'class': f"status status-{report.get('status', '').lower()}"})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Priority: {report.get('priority', 'N/A')}",
                                      attributes={'class': 'report-priority'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Severity: {report.get('severity', 'N/A')}",
                                      attributes={'class': 'report-severity'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Category: {report.get('category', 'N/A')}",
                                      attributes={'class': 'report-category'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Created At: {report.get('created_at', 'N/A')}",
                                      attributes={'class': 'report-created-at'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Resolved At: {report.get('resolved_at', 'N/A')}",
                                      attributes={'class': 'report-resolved-at'})

            self.add_tag('p', parent_selector=report_selector,
                                      content=f"Report Author: {report.get('report_author', 'N/A')}",
                                      attributes={'class': 'report-author'})
        
        if 'company' in self.data:
            company = self.data['company']
            
            self.add_tag('section', parent_selector=report_selector,
                                      attributes={'class': 'company-info'})
            
            self.add_tag('h2', parent_selector=f"{report_selector} .company-info",
                                      content='Company Information',
                                      attributes={'class': 'section-title'})
            
            self.add_tag('p', parent_selector=f"{report_selector} .company-info",
                                      content=f"{company.get('name', 'N/A')} - {company.get('department', 'N/A')}",
                                      attributes={'class': 'company-details'})

            self.add_tag('p', parent_selector=f"{report_selector} .company-info",
                                      content=f"Location: {company.get('location', 'N/A')}",
                                      attributes={'class': 'company-location'})
        
        if 'incident' in self.data:
            incident = self.data['incident']
            
            self.add_tag('section', parent_selector=report_selector,
                                      attributes={'class': 'incident-details'})
            
            self.add_tag('h2', parent_selector=f"{report_selector} .incident-details",
                                      content='Incident Details',
                                      attributes={'class': 'section-title'})
            
            self.add_tag('p', parent_selector=f"{report_selector} .incident-details",
                                      content=incident.get('summary', 'No summary available'),
                                      attributes={'class': 'incident-summary'})

            self.add_tag('p', parent_selector=f"{report_selector} .incident-details",
                                      content=f"Start Time: {incident.get('start_time', 'N/A')}",
                                      attributes={'class': 'incident-start-time'})

            self.add_tag('p', parent_selector=f"{report_selector} .incident-details",
                                      content=f"Detection Time: {incident.get('detection_time', 'N/A')}",
                                      attributes={'class': 'incident-detection-time'})

            self.add_tag('p', parent_selector=f"{report_selector} .incident-details",
                                      content=f"End Time: {incident.get('end_time', 'N/A')}",
                                      attributes={'class': 'incident-end-time'})

            self.add_tag('p', parent_selector=f"{report_selector} .incident-details",
                                      content=f"Root Cause: {incident.get('root_cause', 'N/A')}",
                                      attributes={'class': 'incident-root-cause'})
            
            if 'affected_systems' in incident:
                self.add_tag('ul', parent_selector=f"{report_selector} .incident-details",
                                          attributes={'class': 'affected-systems'})
                
                for system in incident['affected_systems']:
                    self.add_tag('li', parent_selector=f"{report_selector} .affected-systems",
                                              content=system,
                                              attributes={'class': 'system-item'})
        
        if 'impact' in self.data:
            impact = self.data['impact']
            
            self.add_tag('section', parent_selector=report_selector,
                                      attributes={'class': 'impact-metrics'})
            
            self.add_tag('h2', parent_selector=f"{report_selector} .impact-metrics",
                                      content='Impact Analysis',
                                      attributes={'class': 'section-title'})
            
            self.add_tag('div', parent_selector=f"{report_selector} .impact-metrics",
                                      attributes={'class': 'metrics-grid'})
            
            metrics = [
                ('Orders Failed', impact.get('orders_failed', 0)),
                ('Orders Delayed', impact.get('orders_delayed', 0)),
                ('Customers Affected', impact.get('customers_affected', 0)),
                ('Support Tickets', impact.get('support_tickets_created', 0)),
                ('Revenue Loss', f"€{impact.get('estimated_revenue_loss_eur', 0):,}")
            ]
            
            for label, value in metrics:
                self.add_tag('div', parent_selector=f"{report_selector} .metrics-grid",
                                          attributes={'class': 'metric-card'})
                self.add_tag('h3', parent_selector=f"{report_selector} .metrics-grid .metric-card:last-child",
                                          content=label,
                                          attributes={'class': 'metric-label'})
                self.add_tag('p', parent_selector=f"{report_selector} .metrics-grid .metric-card:last-child",
                                          content=str(value),
                                          attributes={'class': 'metric-value'})

        if 'response' in self.data:
            response = self.data['response']

            self.add_tag('section', parent_selector=report_selector,
                                      attributes={'class': 'response-info'})

            self.add_tag('h2', parent_selector=f"{report_selector} .response-info",
                                      content='Response',
                                      attributes={'class': 'section-title'})

            self.add_tag('p', parent_selector=f"{report_selector} .response-info",
                                      content=f"Incident Commander: {response.get('incident_commander', 'N/A')}",
                                      attributes={'class': 'incident-commander'})

            if 'teams_involved' in response:
                self.add_tag('h3', parent_selector=f"{report_selector} .response-info",
                                          content='Teams Involved',
                                          attributes={'class': 'subsection-title'})
                self.add_tag('ul', parent_selector=f"{report_selector} .response-info",
                                          attributes={'class': 'teams-involved'})

                for team in response['teams_involved']:
                    self.add_tag('li', parent_selector=f"{report_selector} .teams-involved",
                                              content=team,
                                              attributes={'class': 'team-item'})

            if 'timeline' in response:
                self.add_tag('h3', parent_selector=f"{report_selector} .response-info",
                                          content='Timeline',
                                          attributes={'class': 'subsection-title'})
                self.add_tag('ul', parent_selector=f"{report_selector} .response-info",
                                          attributes={'class': 'timeline-list'})

                for key in sorted(response['timeline'].keys()):
                    self.add_tag('li', parent_selector=f"{report_selector} .timeline-list",
                                              content=response['timeline'][key],
                                              attributes={'class': 'timeline-item'})

        if 'resolution' in self.data:
            resolution = self.data['resolution']

            self.add_tag('section', parent_selector=report_selector,
                                      attributes={'class': 'resolution-info'})

            self.add_tag('h2', parent_selector=f"{report_selector} .resolution-info",
                                      content='Resolution',
                                      attributes={'class': 'section-title'})

            if 'actions_taken' in resolution:
                self.add_tag('h3', parent_selector=f"{report_selector} .resolution-info",
                                          content='Actions Taken',
                                          attributes={'class': 'subsection-title'})
                self.add_tag('ul', parent_selector=f"{report_selector} .resolution-info",
                                          attributes={'class': 'actions-taken'})

                for action in resolution['actions_taken']:
                    self.add_tag('li', parent_selector=f"{report_selector} .actions-taken",
                                              content=action,
                                              attributes={'class': 'action-item'})

            self.add_tag('p', parent_selector=f"{report_selector} .resolution-info",
                                      content=f"Verification: {resolution.get('verification', 'N/A')}",
                                      attributes={'class': 'resolution-verification'})

            self.add_tag('p', parent_selector=f"{report_selector} .resolution-info",
                                      content=f"Resolved By: {resolution.get('resolved_by', 'N/A')}",
                                      attributes={'class': 'resolved-by'})

        if 'postmortem' in self.data:
            postmortem = self.data['postmortem']

            self.add_tag('section', parent_selector=report_selector,
                                      attributes={'class': 'postmortem-info'})

            self.add_tag('h2', parent_selector=f"{report_selector} .postmortem-info",
                                      content='Postmortem',
                                      attributes={'class': 'section-title'})

            if 'lessons_learned' in postmortem:
                self.add_tag('h3', parent_selector=f"{report_selector} .postmortem-info",
                                          content='Lessons Learned',
                                          attributes={'class': 'subsection-title'})
                self.add_tag('ul', parent_selector=f"{report_selector} .postmortem-info",
                                          attributes={'class': 'lessons-learned'})

                for lesson in postmortem['lessons_learned']:
                    self.add_tag('li', parent_selector=f"{report_selector} .lessons-learned",
                                              content=lesson,
                                              attributes={'class': 'lesson-item'})

            if 'preventive_actions' in postmortem:
                self.add_tag('h3', parent_selector=f"{report_selector} .postmortem-info",
                                          content='Preventive Actions',
                                          attributes={'class': 'subsection-title'})
                self.add_tag('ul', parent_selector=f"{report_selector} .postmortem-info",
                                          attributes={'class': 'preventive-actions'})

                for action in postmortem['preventive_actions']:
                    self.add_tag('li', parent_selector=f"{report_selector} .preventive-actions",
                                              content=action,
                                              attributes={'class': 'preventive-action-item'})

            self.add_tag('p', parent_selector=f"{report_selector} .postmortem-info",
                                      content=f"Review Date: {postmortem.get('review_date', 'N/A')}",
                                      attributes={'class': 'review-date'})
            

        return True
    
    def save_html(self, output_file=None, chart_data=None):
        if self.soup is None:
            raise ValueError("No HTML loaded to save")

        self.inline_stylesheet()

        if chart_data is not None:
            existing_tag = self.soup.select_one('#impact-data')
            if existing_tag:
                existing_tag.decompose()

            script_tag = self.soup.new_tag('script', id='impact-data', type='application/json')
            script_tag.string = json.dumps(chart_data)
            body = self.soup.body

            if body is None:
                raise ValueError("HTML document has no body element")

            body.append(script_tag)
        
        output_path = output_file if output_file else self.html_file

        html_output = str(self.soup)
        html_output = self.minify_html_output(html_output)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_output)


    def inline_stylesheet(self):
        """Inline the template stylesheet into the generated HTML."""
        if self.soup is None:
            return False

        link_tag = self.soup.find('link', rel='stylesheet', href=True)
        if link_tag is None:
            return False

        css_path = os.path.join(self.base_dir, 'incidents', link_tag['href'])

        try:
            with open(css_path, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()

            style_tag = self.soup.new_tag('style')
            style_tag.string = self.safe_css_minify(css_content)
            link_tag.replace_with(style_tag)
            return True
        except Exception as e:
            print(f"Error inlining CSS: {e}")
            return False


    def safe_css_minify(self, css_content: str) -> str:
        try:
            return css_compress(css_content)
        except Exception:
            return css_content


    def safe_js_minify(self, js_content: str) -> str:
        try:
            return jsmin(js_content)
        except Exception:
            return js_content


    def minify_html_output(self, html_content: str) -> str:
        if htmlmin is not None:
            try:
                return htmlmin.minify(html_content, remove_empty_space=True, remove_comments=True)
            except Exception:
                pass

        html_content = re.sub(r'>\s+<', '><', html_content)
        html_content = re.sub(r'\s{2,}', ' ', html_content)
        return html_content.strip()




    def generate_JS(self):
        try:
            index_js_path = os.path.join(self.base_dir, 'JS', 'index.js')

            with open(index_js_path, 'r', encoding='utf-8') as index_js_file:
                index_js_content = index_js_file.read()

            self.add_tag('script', 'body', content=self.safe_js_minify(index_js_content))

            chart_script = self.build_standalone_chart_script()
            self.add_tag('script', 'body', content=self.safe_js_minify(chart_script))
            return True
        except Exception as e:
            print(f'Erreur : ', e)


    def build_standalone_chart_script(self):
        return '''document.addEventListener("DOMContentLoaded", () => {
    const dataScript = document.getElementById("impact-data");
    const canvas = document.getElementById("graph");

    if (!dataScript || !canvas) {
        return;
    }

    let impactData = {};

    try {
        impactData = JSON.parse(dataScript.textContent || "{}");
    } catch (error) {
        console.error("Unable to parse chart data", error);
        return;
    }

    const context = canvas.getContext("2d");
    if (!context) {
        return;
    }

    const entries = Object.entries(impactData).map(([fileName, item]) => ({
        label: fileName.replace(/\.toml$/i, ""),
        value: Number(item && item.estimated_revenue_loss_eur != null ? item.estimated_revenue_loss_eur : 0),
    }));

    const formatCurrency = (value) => `€${Number(value).toLocaleString()}`;

    const resizeCanvas = () => {
        const container = canvas.parentElement;
        const containerWidth = container ? container.clientWidth : 0;
        const width = Math.max(320, Math.floor(containerWidth || canvas.clientWidth || 800));
        const height = Math.max(320, Math.floor(width * 0.42));
        const pixelRatio = window.devicePixelRatio || 1;

        canvas.style.width = "100%";
        canvas.style.height = `${height}px`;
        canvas.width = Math.floor(width * pixelRatio);
        canvas.height = Math.floor(height * pixelRatio);
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);

        return { width, height };
    };

    const drawRoundedRect = (x, y, width, height, radius) => {
        const normalizedRadius = Math.min(radius, width / 2, height / 2);

        context.beginPath();
        context.moveTo(x + normalizedRadius, y);
        context.arcTo(x + width, y, x + width, y + height, normalizedRadius);
        context.arcTo(x + width, y + height, x, y + height, normalizedRadius);
        context.arcTo(x, y + height, x, y, normalizedRadius);
        context.arcTo(x, y, x + width, y, normalizedRadius);
        context.closePath();
    };

    const drawChart = () => {
        const dimensions = resizeCanvas();
        const width = dimensions.width;
        const height = dimensions.height;
        context.clearRect(0, 0, width, height);

        context.fillStyle = "#e6e6e6";
        context.fillRect(0, 0, width, height);

        context.fillStyle = "#000000";
        context.font = "600 18px sans-serif";
        context.textAlign = "left";
        context.textBaseline = "top";
        context.fillText("Estimated Revenue Loss by Incident", 24, 20);

        if (entries.length === 0) {
            context.font = "400 14px sans-serif";
            context.fillText("No chart data available.", 24, 56);
            return;
        }

        const padding = { top: 56, right: 28, bottom: 58, left: 70 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        const maxValue = Math.max(...entries.map((entry) => entry.value), 0);
        const safeMax = maxValue > 0 ? maxValue : 1;
        const axisColor = "#000000";
        const barColor = "rgba(245, 158, 11, 0.82)";
        const barBorder = "rgba(245, 158, 11, 1)";
        const barGap = 16;
        const barWidth = Math.max(24, (chartWidth - barGap * (entries.length - 1)) / entries.length);

        context.strokeStyle = axisColor;
        context.lineWidth = 1;
        context.beginPath();
        context.moveTo(padding.left, padding.top);
        context.lineTo(padding.left, padding.top + chartHeight);
        context.lineTo(padding.left + chartWidth, padding.top + chartHeight);
        context.stroke();

        context.font = "400 12px sans-serif";
        context.fillStyle = "#000000";
        context.textAlign = "right";
        context.textBaseline = "middle";

        const tickCount = 5;
        for (let index = 0; index <= tickCount; index += 1) {
            const ratio = index / tickCount;
            const value = safeMax * (1 - ratio);
            const y = padding.top + chartHeight * ratio;

            context.strokeStyle = axisColor;
            context.beginPath();
            context.moveTo(padding.left - 6, y);
            context.lineTo(padding.left + chartWidth, y);
            context.stroke();

            context.fillText(formatCurrency(value), padding.left - 12, y);
        }

        context.textAlign = "center";
        context.textBaseline = "top";

        entries.forEach((entry, index) => {
            const x = padding.left + index * (barWidth + barGap);
            const barHeight = Math.max(0, (entry.value / safeMax) * (chartHeight - 18));
            const y = padding.top + chartHeight - barHeight;

            context.fillStyle = barColor;
            drawRoundedRect(x, y, barWidth, barHeight, 8);
            context.fill();

            context.strokeStyle = barBorder;
            context.stroke();

            context.fillStyle = "#000000";
            context.font = "600 12px sans-serif";
            context.fillText(formatCurrency(entry.value), x + barWidth / 2, y - 18);

            context.save();
            context.translate(x + barWidth / 2, padding.top + chartHeight + 10);
            context.rotate(-Math.PI / 12);
            context.font = "400 11px sans-serif";
            context.fillStyle = "#000000";
            context.textAlign = "center";
            context.textBaseline = "top";
            context.fillText(entry.label, 0, 0);
            context.restore();
        });
    };

    drawChart();
    window.addEventListener("resize", drawChart);
});'''
        