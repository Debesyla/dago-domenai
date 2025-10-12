INSERT INTO tasks (name, description) VALUES
    ('check_status', 'Check if domain is reachable and return HTTP information'),
    ('check_cms', 'Detect CMS by inspecting HTML, headers, or known signatures'),
    ('check_sitemap', 'Look for sitemap.xml and basic metadata'),
    ('check_company', 'Associate domain with company data'),
    ('analyze_type', 'AI-based classification of domain purpose')
ON CONFLICT (name) DO NOTHING;
