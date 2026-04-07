import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import toml

from paths import BASE_DIR, CONTENT_FOLDER

class TagGenerator:
    def __init__(self, html_file, toml_folder):
        self.html_file = html_file
        self.toml_folder = toml_folder
        self.data = None
        self.infos = None

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
        
        try:
            with open(self.html_file, 'r', encoding='utf-8') as file:
                self.soup = BeautifulSoup(file, 'html.parser')
        except Exception as e:
            print("no html file given", e)

    def add_section(self, product_id, css_class, parent_tag = "body", attributes=None):
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
        
        parent = self.soup.select_one(parent_selector)

        if not parent:
            raise ValueError(f"Parent element '{parent_selector}' not found")
        
        new_tag = self.soup.new_tag(tag_name)
        
        if content:
            new_tag.string = content

        if attributes:
            for key, value in attributes.items():
                new_tag[key] = value
        
        if position == 'append':
            parent.append(new_tag)
        elif position == 'prepend':
            parent.insert(0, new_tag)
        elif position == 'before':
            parent.insert_before(new_tag)
        
        return new_tag
    
    def generate_nav_items(self, files):
        nav_items = []
        for file in files:
            file_id = os.path.splitext(os.path.basename(file))[0]
            
            section_id = f"incident-{file_id}"
            self.add_tag('li', parent_selector='nav ul')
            self.add_tag('a', parent_selector='nav ul li:last-child', content=file_id, attributes={'href': f"#{section_id}"})
        return nav_items
    
    def generate_card_info(self, toml_file):
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
            self.add_tag('button', parent_selector=report_selector,
                                      content='Show Details',
                                      attributes={'class': 'toggle-details-btn', 'data-target': f"#{section_id}-hidden"})   

    def generate_html_from_toml(self, toml_file):
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
    
    def save_html(self, output_file=None):
        if self.soup is None:
            raise ValueError("No HTML loaded to save")
        
        output_path = output_file if output_file else self.html_file
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(str(self.soup.prettify()))




    def generate_JS(self, html_file):
        try:
            attributes= {'src' : '../JS/index.js'}
            self.add_tag('script', 'body', '', attributes)
            return True
        except Exception as e:
            print(f'Erreur : ', e)
        