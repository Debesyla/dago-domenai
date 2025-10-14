# Consolidated Domain Check List & Implementation Plan

This list is categorized by research tier and technical difficulty, providing an actionable roadmap for your tiered development approach.

| Difficulty | Legend |
| :--- | :--- |
| 🟢 | **Easy:** Simple API call or direct HTTP/DNS lookup. |
| 🟡 | **Medium:** Requires parsing, regex, multiple steps, or moderate external data/libraries. |
| 🔴 | **Hard:** Future idea, to be done later. |

---

## Tier 1: Essential Status & Basic Connectivity Checks

### WHOIS Status & Age
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| WHOIS registration status | 🟢 | Query a WHOIS server (e.g., using `python-whois` library) and extract the domain status field. |
| Registrar name and IANA ID | 🟢 | Parse the WHOIS record text to find the 'Registrar' and corresponding IANA ID fields. |
| Registrant organization or person | 🟢 | Extract the 'Registrant Organization' or 'Registrant Name' fields from the WHOIS record. |
| Registration date | 🟢 | Extract the 'Creation Date' field, usually in a standard timestamp format, from the WHOIS record. |
| Expiration date | 🟢 | Extract the 'Registry Expiry Date' field from the WHOIS record. |
| Updated date | 🟢 | Extract the 'Updated Date' or 'Last Modified' field from the WHOIS record. |
| Registry status codes | 🟢 | Extract the list of domain status codes (e.g., `clientTransferProhibited`) from the WHOIS record. |
| Privacy protection enabled | 🟢 | Check if the Registrant/Admin/Tech names contain generic terms like 'Privacy Protection' or 'WhoisGuard'. |
| Domain age | 🟡 | Calculate the difference between the current date and the 'Creation Date' from the WHOIS record. |
| Detect registrar transfers | 🟡 | Check for the presence of multiple 'Registrar' entries in historical WHOIS records. |
| Historical ownership changes | 🔴 | Future idea, to be done later. |
| Detect renewal behavior | 🔴 | Future idea, to be done later. |

### Basic Connectivity & SSL
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| HTTP status code | 🟢 | Make an HTTP GET request and record the final numeric status code (e.g., 200, 404, 301). |
| Final redirect destination | 🟢 | Follow all HTTP redirects and record the final URL after the redirects chain is resolved. |
| Response time | 🟢 | Time the full round-trip of the initial HTTP request until the first byte of the response. |
| HTTPS availability | 🟢 | Attempt to connect to the domain over HTTPS on port 443 and verify success. |
| SSL certificate presence | 🟢 | Check if a valid SSL/TLS certificate is presented during the initial HTTPS handshake. |
| HTTP to HTTPS redirect check | 🟢 | Make an HTTP request to port 80 and verify a redirect to the HTTPS version of the domain. |
| Detect broken layout or redirect loops | 🟡 | Check the redirect chain length and analyze screenshot output for visual errors or loop detection. |

### Core DNS
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| Nameservers list | 🟢 | Query the domain's NS records directly using a DNS resolution library (e.g., `dnspython`). |
| A record IPv4 | 🟢 | Query the domain's A record and return the associated IPv4 address(es). |
| AAAA record IPv6 | 🟢 | Query the domain's AAAA record and return the associated IPv6 address(es). |
| NS records | 🟢 | Query the NS record set to list all authoritative nameservers for the domain. |
| Invalid private IP resolution | 🟡 | Resolve the A/AAAA records and check if the returned IP falls within any private IP range (RFC 1918). |
| Wildcard DNS usage | 🟡 | Query a non-existent subdomain and check if it resolves to the main domain's A record. |

---

## Tier 2: Detailed Technical, Security & Infrastructure

### DNS & Email Security
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| MX records | 🟢 | Query the MX records to list the mail exchange servers and their preference values. |
| TXT records SPF DKIM verification | 🟢 | Query all TXT records and filter for those containing common SPF/DKIM key prefixes. |
| CNAME records | 🟢 | Query the CNAME record for the domain to identify aliases. |
| DMARC policy presence | 🟢 | Query the `\_dmarc` TXT record for existence. |
| DNSSEC enabled | 🟡 | Query the DS (Delegation Signer) record for the domain at its parent zone. |
| Reverse DNS PTR | 🟡 | Query the PTR record for the domain's primary A record IP address. |
| Zone propagation time | 🟡 | Query DNS servers in multiple global regions and measure consistency/lag (requires distributed setup). |
| SPF record valid | 🟡 | Parse the SPF TXT record for syntax and mechanism errors (e.g., too many lookups). |
| DKIM record valid | 🟡 | Query the DKIM selector TXT record and verify the public key syntax. |
| DMARC/DKIM/SPF Audit (Email Auth) | 🟡 | Perform detailed syntax and policy checks across all three email authentication records. |
| BIMI Record Check (Email Branding) | 🟡 | Query the BIMI TXT record and validate the Certificate Authority (VMC) and image URL links. |

### Advanced Security Headers
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| HSTS header presence | 🟢 | Inspect the HTTP response headers for the presence of the `Strict-Transport-Security` header. |
| Referrer-Policy Header Check | 🟢 | Inspect the HTTP response headers for the presence of the `Referrer-Policy` header. |
| X-Content-Type-Options Check | 🟢 | Inspect the HTTP response headers for the presence and correct value (`nosniff`) of this header. |
| Content-Security-Policy (CSP) Check | 🟡 | Inspect the `Content-Security-Policy` header and parse its directives for weak configurations. |
| Permissions-Policy Check | 🟡 | Inspect the `Permissions-Policy` header and check for restrictive values on sensitive features. |
| HSTS Max-Age/Subdomains Check | 🟡 | Check the `max-age` value (should be high) and confirm the `includeSubDomains` directive is present. |

### SSL Deep Dive
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| SSL certificate expiration date | 🟢 | Extract the `notAfter` field from the certificate object obtained during the handshake. |
| SSL issuer | 🟢 | Extract the Certificate Authority (CA) name from the certificate issuer field. |
| SSL validation type DV OV EV | 🟡 | Check the certificate subject fields (Organization, Country) to infer validation type. |
| Certificate chain validity | 🟡 | Check that the entire certificate chain (leaf to root) is present and trusted against a known CA store. |

### Infrastructure & Hosting
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| Response headers snapshot | 🟢 | Capture a full set of response headers (key-value pairs) from the final response. |
| IP country or region | 🟢 | Use a GeoIP database (like MaxMind) to lookup the country and region of the A record IP. |
| Server software detection | 🟡 | Look for `Server` header, common error page fingerprints, and other known signatures. |
| Hosting provider via ASN | 🟡 | Use the IP address and query an IP-to-ASN database to map it to a hosting entity. |
| Cloud hosting detection | 🟡 | Match the ASN, IP ranges, or nameservers against known lists of major cloud providers. |
| CDN usage detection | 🟡 | Match IP ranges or CNAME records against known lists of major CDN providers. |
| Load balancer detection | 🟡 | Perform multiple DNS lookups or HTTP requests to see if different IPs or server headers are returned. |
| Uptime check | 🟡 | Monitor the domain's HTTP status over a prolonged period (e.g., 24 hours) from multiple points. |
| Multiple IPs or failover setup | 🟡 | Check the number of A records returned and, if more than one, perform connectivity checks on all. |
| Map IP geolocation vs declared country | 🟡 | Compare the GeoIP country with the content language or contact info country on the page. |
| Detect foreign hosting | 🟡 | Flag if the IP country is different from the target country (e.g., Lithuanian site hosted in US IP range). |
| Non standard ports open | 🟡 | Perform a quick scan on a list of non-standard high-risk ports (e.g., 8080, 5000, 21, 22). |
| CDN misconfiguration | 🟡 | Request a common static asset and check if it's served through the CDN or directly from the origin. |
| Measure CDN latency | 🟡 | Time the request to a static asset from multiple vantage points (requires distributed setup). |
| Measure time to first byte | 🟡 | Isolate the time taken between the connection being established and the first byte of the response being received. |
| Detect HTTP2 or HTTP3 support | 🟡 | Check the HTTP version negotiation in the handshake or inspect the `Alt-Svc` header. |
| Detect Brotli or Gzip compression | 🟡 | Send an `Accept-Encoding` header and check the `Content-Encoding` header in the response. |

### On-Page Code & Performance
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| HTML title content | 🟢 | Parse the page HTML and extract the text content of the `<title>` tag. |
| Meta description tag | 🟢 | Parse the page HTML and extract the `content` attribute from the `meta name="description"` tag. |
| Content language meta | 🟢 | Extract the value of the `lang` attribute from the `<html>` tag or the `Content-Language` header. |
| Charset encoding | 🟢 | Extract the encoding from the `Content-Type` header or the `<meta charset>` tag. |
| Favicon presence | 🟢 | Check for the presence of the `/favicon.ico` file or a `<link rel="icon">` tag in the HTML. |
| robots.txt existence | 🟢 | Make a GET request to `/robots.txt` and check for a successful (200) status code. |
| sitemap.xml existence | 🟢 | Make a GET request to `/sitemap.xml` and check for a successful (200) status code. |
| Canonical URL tag | 🟢 | Parse the HTML and extract the `href` attribute from the `<link rel="canonical">` tag. |
| Meta noindex or nofollow | 🟢 | Check the `content` attribute of the `meta name="robots"` tag for `noindex` or `nofollow`. |
| Page size bytes | 🟢 | Measure the total byte size of the HTML response body (uncompressed). |
| Compute HTML to text ratio | 🟢 | Calculate the ratio of visible text (stripped of tags) to the total HTML source size. |
| CMS or platform detection | 🟡 | Match common file paths, headers, or HTML source fingerprints against known CMS systems. |
| Technology stack fingerprinting | 🟡 | Match script and stylesheet URLs, headers, and code snippets against a database of known technologies. |
| JavaScript redirect detection | 🟡 | Use a headless browser to render the page and detect JS navigation events. |
| Image count or total media weight | 🟡 | Parse the HTML, count `<img>` tags, and sum the byte sizes of all linked media files. |
| Check for Unminified/Uncompressed Assets | 🟡 | Scan `<script>` and `<link>` URLs for common unminified file names (e.g., `.js`, `.css` without `.min`). |
| Detect JS heavy sites | 🟡 | Calculate the ratio of JavaScript file size to the total page size or the DOM size. |
| Detect SPA or lazy loading | 🟡 | Analyze script content or observe network requests for tell-tale signs of single-page application frameworks. |
| Detect AMP pages | 🟡 | Check for the presence of the AMP boilerplate code or the `<html> ⚡` attribute. |
| Detect site generator type | 🟡 | Look for comment lines like `` or generator meta tags. |

---

## Tier 3: Content, Compliance, Fingerprinting & Business Analysis

### Security Vulnerabilities
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| HTTP header misconfigurations | 🟡 | Cross-reference captured headers against OWASP security header best practice lists. |
| Outdated framework or CMS version | 🟡 | Use fingerprinting results (CMS/Tech) and compare versions against known vulnerability databases. |
| Exposed git or env files | 🟡 | Attempt requests to common, sensitive paths like `/.git/HEAD`, `/wp-config.php`, or `/.env`. |
| Detect VPN or proxy IP hosting | 🟡 | Use the IP address and check it against known public lists of VPN/Proxy/Tor exit nodes. |
| Blacklist presence | 🟡 | Query the domain/IP against known DNS-based blackhole lists (DNSBLs) and reputation services. |
| Phishing or malware flags | 🟡 | Query the domain against Google Safe Browsing API or other security vendor APIs. |
| TLS fingerprint reuse | 🔴 | Future idea, to be done later. |
| Detect redirector or spam nodes | 🔴 | Future idea, to be done later. |
| Fast flux DNS pattern | 🔴 | Future idea, to be done later. |

### SEO & Traffic Analysis
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| URL Slug Cleanliness Check (Underscores/Parameters) | 🟢 | Scan the final URL for the presence of underscores (`_`) or excessive query parameters. |
| Web archive presence | 🟡 | Check for successful API responses from archive services like Archive.org for recent snapshots. |
| Indexed in Google | 🟡 | Use a search operator (e.g., `site:example.com`) and check for successful results (requires a scraping proxy). |
| Crawl Depth Audit (Page Proximity) | 🟡 | Crawl a small subset of the site and calculate the minimum clicks from the homepage to each page. |
| Identify Orphaned Pages | 🟡 | Compare all pages found in the sitemap against pages discovered via crawling. |
| Detect Zombie Pages (Thin Content) | 🟡 | Flag pages with low word count, low traffic (requires external data), or no internal links. |
| Structured Data Implementation Correctness | 🟡 | Extract schema markup (JSON-LD, etc.) and validate against schema.org and Google's guidelines. |
| Historical redirects | 🔴 | Future idea, to be done later. |
| SEO metrics backlinks count | 🔴 | Future idea, to be done later. |
| EEAT Signal Assessment (Author Credibility) | 🔴 | Future idea, to be done later. |

### Business & Compliance
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| Social media links on homepage | 🟡 | Scrape the HTML for common social media URLs (Facebook, LinkedIn, X, etc.). |
| Analytics tags | 🟡 | Scan the HTML source for common tracking codes (GA, Meta, AdSense) or known tag manager scripts. |
| Cookie banner or GDPR compliance | 🟡 | Use a headless browser to detect common cookie consent banners, overlays, or pop-ups. |
| Detect contact info presence | 🟡 | Scrape common areas (header, footer, contact page) for email addresses, phone numbers, and addresses. |
| Detect company code or VAT number | 🟡 | Use regex to scan the footer/about page for patterns matching Lithuanian company/VAT codes. |
| Detect cookie consent mechanism | 🟡 | Check for the presence of common consent management platform (CMP) scripts (e.g., OneTrust, Cookiebot). |
| Detect currency usage | 🟡 | Scan the visible content for common currency symbols or ISO codes (e.g., €, USD, LT). |
| Detect Lithuanian city mentions | 🟡 | Scan the page text and contact info against a list of common Lithuanian city names. |
| Detect one page vs multipage sites | 🟡 | Crawl the homepage and check the total number of internally linked unique pages found. |
| Detect privacy focused technology | 🟡 | Scan for scripts and headers related to privacy-enhancing tech or alternative analytics platforms. |
| Link to Lithuanian business register | 🔴 | Future idea, to be done later. |

### Content & Language Analysis
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| Extract external links from homepage | 🟢 | Parse the HTML and extract all `href` attributes from `<a>` tags pointing to other domains. |
| Emoji presence in domain or content | 🟢 | Scan the URL and extracted text content for the presence of common emoji characters. |
| Keyword extraction | 🟡 | Use a simple NLP library (NLTK/spaCy) to identify the top N-grams and keywords from the text content. |
| Extract main website topics | 🟡 | Apply a basic keyword clustering algorithm or use a simple topic model on the extracted text. |
| Detect Lithuanian audience targeting | 🟡 | Check for Lithuanian language, currency, business links, and city mentions. |
| Detect language variants | 🟡 | Use language detection libraries on the body text to confirm the declared language. |
| Detect translation or multilingual setup | 🟡 | Check for common language-switcher elements, URL path prefixes (`/en/`, `/lt/`), or Hreflang tags. |
| Detect social proof elements | 🟡 | Look for HTML patterns indicative of testimonials, review scores, trust badges, or subscriber counts. |
| Detect affiliate links or ads | 🟡 | Scan external link URLs for common affiliate parameters or ad network domains. |
| Detect cross country targeting | 🟡 | Check for the presence of Hreflang tags, specific geo-targeting settings, or conflicting language/IP info. |
| Detect language mix | 🟡 | Use language detection on different sections of the page to check if multiple languages are present. |
| Detect Lithuanian vs English word ratio | 🟡 | Run language detection per word/sentence to calculate the percentage mix of the two languages. |
| Detect AI chatbot presence | 🟡 | Scan for common JavaScript library names (e.g., Intercom, Tawk.to, Drift) or specific div IDs/classes. |
| Detect tone or sentiment of content | 🔴 | Future idea, to be done later. |
| Extract semantic keywords for trend reports | 🔴 | Future idea, to be done later. |
| Detect humor or satire websites | 🔴 | Future idea, to be done later. |
| Detect open API endpoints | 🔴 | Future idea, to be done later. |
| Detect blockchain or crypto payments | 🔴 | Future idea, to be done later. |
| Detect NFTs or ENS mentions | 🔴 | Future idea, to be done later. |

### AI & Advanced Content Detection
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| AI category classification | 🔴 | Future idea, to be done later. |
| Detect AI generated content | 🔴 | Future idea, to be done later. |
| Detect AI generated logos | 🔴 | Future idea, to be done later. |
| Detect stock template websites | 🔴 | Future idea, to be done later. |
| Detect web age aesthetic | 🔴 | Future idea, to be done later. |

### Digital Fingerprinting & Brand
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| Homepage HTML hash | 🟢 | Compute a cryptographic hash (e.g., SHA-256) of the raw HTML source code. |
| Detect favicon hash | 🟢 | Calculate the hash of the favicon file content after downloading it. |
| Screenshot capture | 🟡 | Use a headless browser (Playwright) to capture a full-page screenshot (requires significant resources). |
| Detect language mismatch | 🟡 | Compare the HTML `lang` attribute against the content's detected language. |
| Browser Fingerprinting Vectors Scan | 🔴 | Future idea, to be done later. |
| Logo extraction | 🔴 | Future idea, to be done later. |
| Screenshot AI tagging | 🔴 | Future idea, to be done later. |
| Extract brand color palette | 🔴 | Future idea, to be done later. |

### Domain Value & Monetization
| Check | Difficulty | How to Perform the Check |
| :--- | :--- | :--- |
| Detect parked or for sale pages | 🟡 | Match screenshot/HTML content against known templates and keywords used by domain parking/for-sale services. |
| Detect for sale banners | 🟡 | Look for specific keywords (e.g., "for sale," "this domain," "offers accepted") in large fonts or header banners. |
| Estimate domain value | 🔴 | Future idea, to be done later. |
| Detect parking provider fingerprint | 🔴 | Future idea, to be done later. |
| Detect drop catching activity | 🔴 | Future idea, to be done later. |
| Detect domain marketplace listings | 🔴 | Future idea, to be done later. |
| Detect reactivated expired domains | 🔴 | Future idea, to be done later. |
| Estimate keyword commercial intent | 🔴 | Future idea, to be done later. |
| Detect premium keyword patterns | 🔴 | Future idea, to be done later. |
| Detect brandable name patterns | 🔴 | Future idea, to be done later. |
| Detect new registration trends | 🔴 | Future idea, to be done later. |

---

## Shared Infrastructure & Portfolio Clustering

### Clustering & Portfolio
| Check                                                    | Difficulty | How to Perform the Check                                                                     |
| :------------------------------------------------------- | :--------- | :------------------------------------------------------------------------------------------- |
| Detect shared IPs                                        | 🟡         | Group domains in your database by their resolved IP address (A record).                      |
| Detect shared analytics IDs                              | 🟡         | Group domains by the extracted Google Analytics (GA) or other tracking ID found in the HTML. |
| Detect ownership via SSL organization                    | 🟡         | Group domains by the Organization Name field extracted from their SSL certificates.          |
| Detect shared hosting clusters                           | 🟡         | Group domains by their common IP subnet (e.g., first three octets of the IPv4 address).      |
| Detect domain clusters by favicon                        | 🟡         | Group domains by their computed favicon hash.                                                |
| Detect groups by CSS JS library                          | 🟡         | Group domains by identical or similar lists of CSS/JS library file URLs.                     |
| Detect shared Google Fonts usage                         | 🟡         | Group domains by identical or similar lists of Google Fonts URLs in the HTML.                |
| Detect same registrar plus nameservers plus SSL clusters | 🔴         | Future idea, to be done later.                                                               |
| Detect domain portfolios                                 | 🔴         | Future idea, to be done later.                                                               |
| Build domain IP SSL registrar graph                      | 🔴         | Future idea, to be done later.                                                               |
| Detect interlinking clusters                             | 🔴         | Future idea, to be done later.                                                               |
| Detect shared contact email addresses                    | 🔴         | Future idea, to be done later.                                                               |
| Detect same Cloudflare account                           | 🔴         | Future idea, to be done later.                                                               |

