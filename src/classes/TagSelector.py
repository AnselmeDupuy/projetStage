import toml

class TagSelector:
    def __init__(self, toml_file, tag_generator):
        self.toml_file = toml_file
        self.tag_generator = tag_generator
        self.data = None
    
    def load_toml(self):
        with open(self.toml_file, 'r', encoding='utf-8') as f:
            self.data = toml.load(f)
        return self.data
    
    def generate_html_from_toml(self):
        if not self.data:
            self.load_toml()
        
        self.tag_generator.add_tag('div', parent_selector='body', 
                                   attributes={'class': 'incident-report', 'id': 'report-container'})
        
        if 'report' in self.data:
            report = self.data['report']
            
            self.tag_generator.add_tag('header', parent_selector='.incident-report', 
                                      attributes={'class': 'report-header'})
            
            self.tag_generator.add_tag('h1', parent_selector='.report-header', 
                                      content=report.get('title', 'Incident Report'),
                                      attributes={'class': 'report-title'})
            
            self.tag_generator.add_tag('div', parent_selector='.report-header', 
                                      attributes={'class': 'meta-info'})
            
            self.tag_generator.add_tag('span', parent_selector='.meta-info', 
                                      content=f"Ticket: {report.get('ticket_id', 'N/A')}",
                                      attributes={'class': 'ticket-id'})
            
            self.tag_generator.add_tag('span', parent_selector='.meta-info', 
                                      content=f"Status: {report.get('status', 'Unknown')}",
                                      attributes={'class': f"status status-{report.get('status', '').lower()}"})
        
        if 'company' in self.data:
            company = self.data['company']
            
            self.tag_generator.add_tag('section', parent_selector='.incident-report', 
                                      attributes={'class': 'company-info'})
            
            self.tag_generator.add_tag('h2', parent_selector='.company-info', 
                                      content='Company Information',
                                      attributes={'class': 'section-title'})
            
            self.tag_generator.add_tag('p', parent_selector='.company-info', 
                                      content=f"{company.get('name', 'N/A')} - {company.get('department', 'N/A')}",
                                      attributes={'class': 'company-details'})
        
        if 'incident' in self.data:
            incident = self.data['incident']
            
            self.tag_generator.add_tag('section', parent_selector='.incident-report', 
                                      attributes={'class': 'incident-details'})
            
            self.tag_generator.add_tag('h2', parent_selector='.incident-details', 
                                      content='Incident Details',
                                      attributes={'class': 'section-title'})
            
            self.tag_generator.add_tag('p', parent_selector='.incident-details', 
                                      content=incident.get('summary', 'No summary available'),
                                      attributes={'class': 'incident-summary'})
            
            if 'affected_systems' in incident:
                self.tag_generator.add_tag('ul', parent_selector='.incident-details', 
                                          attributes={'class': 'affected-systems'})
                
                for system in incident['affected_systems']:
                    self.tag_generator.add_tag('li', parent_selector='.affected-systems', 
                                              content=system,
                                              attributes={'class': 'system-item'})
        
        if 'impact' in self.data:
            impact = self.data['impact']
            
            self.tag_generator.add_tag('section', parent_selector='.incident-report', 
                                      attributes={'class': 'impact-metrics'})
            
            self.tag_generator.add_tag('h2', parent_selector='.impact-metrics', 
                                      content='Impact Analysis',
                                      attributes={'class': 'section-title'})
            
            self.tag_generator.add_tag('div', parent_selector='.impact-metrics', 
                                      attributes={'class': 'metrics-grid'})
            
            metrics = [
                ('Orders Failed', impact.get('orders_failed', 0)),
                ('Customers Affected', impact.get('customers_affected', 0)),
                ('Revenue Loss', f"€{impact.get('estimated_revenue_loss_eur', 0):,}")
            ]
            
            for label, value in metrics:
                self.tag_generator.add_tag('div', parent_selector='.metrics-grid', 
                                          attributes={'class': 'metric-card'})

        return True
