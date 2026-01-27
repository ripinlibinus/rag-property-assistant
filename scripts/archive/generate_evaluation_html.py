"""
Generate HTML Evaluation Interface

Creates an interactive HTML file for easier manual evaluation.
Much more user-friendly than editing CSV directly.

Features:
- Each property result has clickable relevant/not relevant buttons
- URLs are clickable (opens in new tab)
- Auto-calculates relevant count from individual ratings

Usage:
    python scripts/generate_evaluation_html.py
    python scripts/generate_evaluation_html.py --input data/evaluation/test_results_latest.json
"""

import json
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_properties_from_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse individual property results from agent response.

    Returns list of dicts with: title, url, details, specs
    """
    properties = []

    # Pattern for numbered items with property info
    # Match patterns like:
    # 1. **Title**
    # or just numbered lists

    # Split by numbered items (1., 2., **1.**, etc.)
    items = re.split(r'\n\s*(?:\*\*)?(\d+)\.(?:\*\*)?\s*', response)

    # First item is intro text, skip it
    # Then pairs of (number, content)
    for i in range(1, len(items), 2):
        if i + 1 < len(items):
            num = items[i]
            content = items[i + 1].strip()

            if not content:
                continue

            # Extract title (first line, usually in bold **)
            lines = content.split('\n')
            title_match = re.match(r'\*\*(.+?)\*\*', lines[0])
            title = title_match.group(1) if title_match else lines[0][:100]

            # Extract URL
            url_match = re.search(r'\[Lihat Detail\]\((https?://[^\)]+)\)', content)
            if not url_match:
                url_match = re.search(r'(https?://[^\s\)]+)', content)
            url = url_match.group(1) if url_match else None

            # Extract price
            price_match = re.search(r'Rp\s*([\d\.,]+)', content)
            price = f"Rp {price_match.group(1)}" if price_match else ""

            # Extract location (line with 📍 or after "Lokasi:")
            location = ""
            for line in lines:
                if '📍' in line or 'lokasi' in line.lower():
                    location = re.sub(r'^[📍🏠💰🛏️🚿📐🔗\s]+', '', line).strip()
                    break

            # Extract specs (kamar tidur, kamar mandi, LT, LB)
            specs = []

            # Bedrooms
            bedroom_match = re.search(r'(\d+)\s*[Kk]amar\s*[Tt]idur', content)
            if bedroom_match:
                specs.append(f"{bedroom_match.group(1)} KT")

            # Bathrooms
            bathroom_match = re.search(r'(\d+)\s*[Kk]amar\s*[Mm]andi', content)
            if bathroom_match:
                specs.append(f"{bathroom_match.group(1)} KM")

            # Land area (LT)
            lt_match = re.search(r'LT\s*[:\s]*(\d+)\s*m', content, re.IGNORECASE)
            if lt_match:
                specs.append(f"LT {lt_match.group(1)}m²")

            # Building area (LB)
            lb_match = re.search(r'LB\s*[:\s]*(\d+)\s*m', content, re.IGNORECASE)
            if lb_match:
                specs.append(f"LB {lb_match.group(1)}m²")

            # Floors
            floor_match = re.search(r'(\d+)\s*[Ll]antai', content)
            if floor_match:
                specs.append(f"{floor_match.group(1)} Lantai")

            # Certificate type
            cert_match = re.search(r'(SHM|SHGB|HGB|AJB|Girik)', content, re.IGNORECASE)
            if cert_match:
                specs.append(cert_match.group(1).upper())

            # Property type badge based on source and listing_type:
            # 1. source = "project" → Primary (indicated by 🏗️ Proyek Baru)
            # 2. source = "listing" + listing_type = "rent" → Rent (title has Sewa/Disewa/Disewakan)
            # 3. source = "listing" + listing_type = "sale" → Secondary (default for Resale)

            # Check for Primary (project source)
            if re.search(r'🏗️|Proyek Baru|\bProyek\b|\bproject\b', content, re.IGNORECASE):
                prop_type = 'Primary'
            # Check for Rent (listing with rent type) - title usually has Disewakan/Sewa
            elif re.search(r'\b(Sewa|Disewa|Disewakan)\b', content, re.IGNORECASE):
                prop_type = 'Rent'
            # Check for Secondary (listing with sale type) - indicated by Resale or Dijual
            elif re.search(r'🔄|Resale|\b(Jual|Dijual)\b', content, re.IGNORECASE):
                prop_type = 'Secondary'
            else:
                prop_type = ""

            # Clean up details (remove markdown, keep key info)
            details = content[:300] if len(content) > 300 else content

            properties.append({
                'num': num,
                'title': title.strip(),
                'url': url,
                'price': price,
                'location': location,
                'specs': specs,
                'prop_type': prop_type,
                'details': details
            })

    return properties


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Evaluation - {timestamp}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
            color: #fff;
        }}
        header p {{
            color: rgba(255,255,255,0.8) !important;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        .stat {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 12px 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #fff;
        }}
        .stat-label {{
            font-size: 12px;
            color: rgba(255,255,255,0.7);
            text-transform: uppercase;
        }}
        .controls {{
            background: #fff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .controls button {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .btn-export {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: #fff;
        }}
        .btn-export:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        }}
        .btn-save {{
            background: #27ae60;
            color: white;
        }}
        .btn-save:hover {{
            background: #219a52;
        }}
        .btn-load {{
            background: #9b59b6;
            color: white;
        }}
        .btn-load:hover {{
            background: #8e44ad;
        }}
        .filter-group {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-left: auto;
        }}
        .filter-group label {{
            font-size: 13px;
            color: #666;
        }}
        .filter-group select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fff;
            color: #333;
            font-size: 13px;
        }}
        .progress-bar {{
            height: 6px;
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
            margin-top: 15px;
            overflow: hidden;
        }}
        .progress-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            border-radius: 3px;
            transition: width 0.3s;
        }}

        /* Query Card */
        .query-card {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .query-card.rated {{
            border-color: #27ae60;
            border-width: 2px;
        }}
        .query-header {{
            background: linear-gradient(135deg, #34495e, #2c3e50);
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .query-header.rated {{
            background: linear-gradient(135deg, #27ae60, #219a52);
        }}
        .query-id {{
            background: #fff;
            color: #2c3e50;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        }}
        .query-text {{
            flex: 1;
            font-size: 16px;
            min-width: 200px;
            color: white;
        }}
        .query-meta {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .category-tag {{
            background: rgba(255,255,255,0.2);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            color: rgba(255,255,255,0.9);
        }}
        .results-badge {{
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .results-badge.has-results {{
            background: #2ecc71;
            color: white;
        }}
        .results-badge.no-results {{
            background: #e74c3c;
            color: white;
        }}

        /* Property Items */
        .query-body {{
            padding: 20px;
            background: #fafafa;
        }}
        .property-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .property-item {{
            background: #fff;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            display: flex;
            gap: 15px;
            align-items: flex-start;
            transition: all 0.2s;
        }}
        .property-item.relevant {{
            border-color: #27ae60;
            background: rgba(39, 174, 96, 0.08);
        }}
        .property-item.not-relevant {{
            border-color: #e74c3c;
            background: rgba(231, 76, 60, 0.08);
            opacity: 0.7;
        }}
        .property-num {{
            background: #3498db;
            color: #fff;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .property-content {{
            flex: 1;
            min-width: 0;
        }}
        .property-title {{
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 5px;
            color: #333;
        }}
        .property-title a {{
            color: #2980b9;
            text-decoration: none;
        }}
        .property-title a:hover {{
            text-decoration: underline;
            color: #3498db;
        }}
        .property-info {{
            font-size: 13px;
            color: #666;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .property-info span {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .property-specs {{
            font-size: 13px;
            color: #666;
            margin-top: 4px;
        }}
        .prop-type-badge {{
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 3px;
            margin-left: 8px;
            font-weight: 500;
            text-transform: uppercase;
        }}
        .prop-type-badge.type-primary {{
            background: #3498db;
            color: white;
        }}
        .prop-type-badge.type-secondary {{
            background: #27ae60;
            color: white;
        }}
        .prop-type-badge.type-rent {{
            background: #f39c12;
            color: white;
        }}
        .beyond-badge {{
            font-size: 9px;
            padding: 2px 5px;
            border-radius: 3px;
            background: #95a5a6;
            color: white;
            margin-left: 8px;
            font-weight: normal;
        }}
        .property-actions {{
            display: flex;
            gap: 8px;
            flex-shrink: 0;
        }}
        .btn-relevant, .btn-not-relevant {{
            width: 40px;
            height: 40px;
            border: 2px solid;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 20px;
            transition: all 0.2s;
            background: transparent;
        }}
        .btn-relevant {{
            border-color: #27ae60;
            color: #27ae60;
        }}
        .btn-relevant:hover, .btn-relevant.active {{
            background: #27ae60;
            color: white;
        }}
        .btn-not-relevant {{
            border-color: #e74c3c;
            color: #e74c3c;
        }}
        .btn-not-relevant:hover, .btn-not-relevant.active {{
            background: #e74c3c;
            color: white;
        }}

        /* Rating Section */
        .rating-section {{
            margin-top: 20px;
            padding: 20px;
            background: #fff;
            border-top: 1px solid #e0e0e0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        .rating-field {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .rating-field label {{
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
            font-weight: 500;
        }}
        .rating-field .value {{
            font-size: 20px;
            font-weight: bold;
            color: #2980b9;
        }}
        .rating-field select,
        .rating-field textarea {{
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fff;
            color: #333;
            font-size: 14px;
        }}
        .rating-field select:focus,
        .rating-field textarea:focus {{
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }}
        .rating-field textarea {{
            resize: vertical;
            min-height: 50px;
        }}

        /* Raw response (collapsed) */
        .raw-response {{
            margin-top: 15px;
            padding: 0 20px 20px 20px;
        }}
        .raw-toggle {{
            background: #f5f5f5;
            border: 1px solid #ddd;
            color: #666;
            padding: 8px 15px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .raw-toggle:hover {{
            border-color: #3498db;
            color: #3498db;
            background: #fff;
        }}
        .raw-content {{
            margin-top: 10px;
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            white-space: pre-wrap;
            font-size: 13px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            max-height: 300px;
            overflow-y: auto;
            display: none;
            color: #333;
        }}
        .raw-content.show {{
            display: block;
        }}

        .hidden {{
            display: none !important;
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #f0f0f0;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #ccc;
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #aaa;
        }}

        @media (max-width: 768px) {{
            .query-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .filter-group {{
                margin-left: 0;
                width: 100%;
            }}
            .property-item {{
                flex-direction: column;
            }}
            .property-actions {{
                width: 100%;
                justify-content: flex-end;
            }}
            .rating-section {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>RAG Property Chatbot - Evaluation Interface</h1>
            <p style="color: #888;">Test: {timestamp} | Click ✓ or ✗ on each property to rate relevance</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_queries}</div>
                    <div class="stat-label">Total Queries</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="rated-count">0</div>
                    <div class="stat-label">Rated</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="remaining-count">{total_queries}</div>
                    <div class="stat-label">Remaining</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="avg-overall-precision">-</div>
                    <div class="stat-label">Avg Overall P</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="avg-precision">-</div>
                    <div class="stat-label">Avg P@5</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="avg-mrr">-</div>
                    <div class="stat-label">MRR</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="success-rate">-</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill" id="progress-fill" style="width: 0%"></div>
            </div>
        </header>

        <div class="controls">
            <button class="btn-export" onclick="exportResults()">📥 Export to CSV</button>
            <button class="btn-save" onclick="saveToLocalStorage()">💾 Save Progress</button>
            <button class="btn-load" onclick="loadFromLocalStorage()">📂 Load Progress</button>
            <div class="filter-group">
                <label>Category:</label>
                <select id="filter-category" onchange="filterCards()">
                    <option value="">All</option>
                    {category_options}
                </select>
            </div>
            <div class="filter-group">
                <label>Status:</label>
                <select id="filter-rated" onchange="filterCards()">
                    <option value="">All</option>
                    <option value="rated">Rated</option>
                    <option value="unrated">Unrated</option>
                </select>
            </div>
        </div>

        <div id="cards-container">
            {cards_html}
        </div>
    </div>

    <script>
        // Store results
        const results = {results_json};
        const propertyRatings = {{}};  // queryId -> {{propNum: 'relevant'/'not-relevant'}}

        function toggleRelevance(queryId, propNum, isRelevant) {{
            const key = `${{queryId}}_${{propNum}}`;
            const item = document.querySelector(`[data-prop-key="${{key}}"]`);
            const btnRelevant = item.querySelector('.btn-relevant');
            const btnNotRelevant = item.querySelector('.btn-not-relevant');

            if (!propertyRatings[queryId]) {{
                propertyRatings[queryId] = {{}};
            }}

            // Toggle logic
            const currentRating = propertyRatings[queryId][propNum];

            if (isRelevant) {{
                if (currentRating === 'relevant') {{
                    // Unset
                    delete propertyRatings[queryId][propNum];
                    item.classList.remove('relevant', 'not-relevant');
                    btnRelevant.classList.remove('active');
                }} else {{
                    propertyRatings[queryId][propNum] = 'relevant';
                    item.classList.remove('not-relevant');
                    item.classList.add('relevant');
                    btnRelevant.classList.add('active');
                    btnNotRelevant.classList.remove('active');
                }}
            }} else {{
                if (currentRating === 'not-relevant') {{
                    // Unset
                    delete propertyRatings[queryId][propNum];
                    item.classList.remove('relevant', 'not-relevant');
                    btnNotRelevant.classList.remove('active');
                }} else {{
                    propertyRatings[queryId][propNum] = 'not-relevant';
                    item.classList.remove('relevant');
                    item.classList.add('not-relevant');
                    btnNotRelevant.classList.add('active');
                    btnRelevant.classList.remove('active');
                }}
            }}

            updateQueryStats(queryId);
            updateGlobalStats();
        }}

        function updateQueryStats(queryId) {{
            const card = document.querySelector(`[data-query-id="${{queryId}}"]`);
            const ratings = propertyRatings[queryId] || {{}};

            // Count relevant in first 5 results only (for Precision@5)
            let relevantInTop5 = 0;
            let totalRelevant = 0;
            let firstRelevantRank = 0;  // 0 means no relevant found
            for (let i = 1; i <= 10; i++) {{
                const rating = ratings[String(i)];
                if (rating === 'relevant') {{
                    totalRelevant++;
                    if (firstRelevantRank === 0) {{
                        firstRelevantRank = i;  // First relevant position
                    }}
                    if (i <= 5) {{
                        relevantInTop5++;
                    }}
                }}
            }}

            const totalRated = Object.keys(ratings).length;
            const totalProps = card.querySelectorAll('.property-item').length;

            // Update relevant count display (show total relevant)
            const relevantDisplay = card.querySelector('.relevant-count-display');
            if (relevantDisplay) {{
                relevantDisplay.textContent = totalRelevant;
            }}

            // Update first relevant rank display
            const firstRelevantDisplay = card.querySelector('.first-relevant-display');
            if (firstRelevantDisplay) {{
                firstRelevantDisplay.textContent = firstRelevantRank > 0 ? '#' + firstRelevantRank : '-';
            }}

            // Calculate overall precision (all results)
            const resultsCount = parseInt(card.dataset.resultsCount) || 0;
            let overallPrecision = '-';
            if (resultsCount > 0 && totalRated > 0) {{
                overallPrecision = ((totalRelevant / resultsCount) * 100).toFixed(0) + '%';
            }}
            const overallPrecisionDisplay = card.querySelector('.overall-precision-display');
            if (overallPrecisionDisplay) {{
                overallPrecisionDisplay.textContent = overallPrecision;
            }}

            // Calculate precision@5 (only top 5 results)
            const denominator = Math.min(resultsCount, 5);
            let precision = '-';
            if (denominator > 0 && totalRated > 0) {{
                // Use relevantInTop5 (capped at denominator) for precision
                const numerator = Math.min(relevantInTop5, denominator);
                precision = ((numerator / denominator) * 100).toFixed(0) + '%';
            }}
            const precisionDisplay = card.querySelector('.precision-display');
            if (precisionDisplay) {{
                precisionDisplay.textContent = precision;
            }}

            // Calculate MRR (reciprocal rank)
            let mrr = '-';
            if (totalRated > 0) {{
                if (firstRelevantRank > 0) {{
                    mrr = (1 / firstRelevantRank).toFixed(3);
                }} else {{
                    mrr = '0.000';
                }}
            }}
            const mrrDisplay = card.querySelector('.mrr-display');
            if (mrrDisplay) {{
                mrrDisplay.textContent = mrr;
            }}

            // Calculate Success (Binary: 1 if any relevant, 0 otherwise)
            let success = '-';
            if (totalRated > 0) {{
                success = totalRelevant >= 1 ? '✓ Yes' : '✗ No';
            }}
            const successDisplay = card.querySelector('.success-display');
            if (successDisplay) {{
                successDisplay.textContent = success;
                successDisplay.style.color = totalRelevant >= 1 ? '#27ae60' : '#e74c3c';
            }}

            // Mark card as rated if all properties are rated
            const header = card.querySelector('.query-header');
            if (totalRated === totalProps && totalProps > 0) {{
                header.classList.add('rated');
                card.classList.add('rated');
            }} else {{
                header.classList.remove('rated');
                card.classList.remove('rated');
            }}
        }}

        function updateGlobalStats() {{
            let totalRated = 0;
            let totalPrecisionAt5 = 0;
            let totalOverallPrecision = 0;
            let totalMRR = 0;
            let totalSuccess = 0;
            let precisionAt5Count = 0;
            let overallPrecisionCount = 0;
            let mrrCount = 0;

            document.querySelectorAll('.query-card').forEach(card => {{
                const queryId = card.dataset.queryId;
                const ratings = propertyRatings[queryId] || {{}};
                const totalProps = card.querySelectorAll('.property-item').length;
                const totalRatedInQuery = Object.keys(ratings).length;

                if (totalRatedInQuery === totalProps && totalProps > 0) {{
                    totalRated++;

                    const resultsCount = parseInt(card.dataset.resultsCount) || 0;

                    // Count total relevant, relevant in top 5, and first relevant rank
                    let totalRelevant = 0;
                    let relevantInTop5 = 0;
                    let firstRelevantRank = 0;
                    for (let i = 1; i <= 10; i++) {{
                        if (ratings[String(i)] === 'relevant') {{
                            totalRelevant++;
                            if (firstRelevantRank === 0) {{
                                firstRelevantRank = i;
                            }}
                            if (i <= 5) {{
                                relevantInTop5++;
                            }}
                        }}
                    }}

                    // Calculate overall precision
                    if (resultsCount > 0) {{
                        totalOverallPrecision += totalRelevant / resultsCount;
                        overallPrecisionCount++;
                    }}

                    // Calculate precision@5
                    const denominator = Math.min(resultsCount, 5);
                    if (denominator > 0) {{
                        const numerator = Math.min(relevantInTop5, denominator);
                        totalPrecisionAt5 += numerator / denominator;
                        precisionAt5Count++;
                    }}

                    // Calculate MRR (only for queries with results)
                    if (resultsCount > 0) {{
                        if (firstRelevantRank > 0) {{
                            totalMRR += 1 / firstRelevantRank;
                        }}
                        // If no relevant found, MRR contribution is 0
                        mrrCount++;
                    }}

                    // Calculate Success (binary)
                    if (totalRelevant >= 1) {{
                        totalSuccess++;
                    }}
                }}
            }});

            document.getElementById('rated-count').textContent = totalRated;
            document.getElementById('remaining-count').textContent = {total_queries} - totalRated;
            document.getElementById('progress-fill').style.width = (totalRated / {total_queries} * 100) + '%';

            // Display average overall precision
            if (overallPrecisionCount > 0) {{
                document.getElementById('avg-overall-precision').textContent = ((totalOverallPrecision / overallPrecisionCount) * 100).toFixed(1) + '%';
            }} else {{
                document.getElementById('avg-overall-precision').textContent = '-';
            }}

            // Display average precision@5
            if (precisionAt5Count > 0) {{
                document.getElementById('avg-precision').textContent = ((totalPrecisionAt5 / precisionAt5Count) * 100).toFixed(1) + '%';
            }} else {{
                document.getElementById('avg-precision').textContent = '-';
            }}

            // Display MRR
            if (mrrCount > 0) {{
                document.getElementById('avg-mrr').textContent = (totalMRR / mrrCount).toFixed(3);
            }} else {{
                document.getElementById('avg-mrr').textContent = '-';
            }}

            // Display Success Rate
            if (totalRated > 0) {{
                document.getElementById('success-rate').textContent = ((totalSuccess / totalRated) * 100).toFixed(1) + '%';
            }} else {{
                document.getElementById('success-rate').textContent = '-';
            }}
        }}

        function toggleRawResponse(queryId) {{
            const content = document.querySelector(`#raw-${{queryId}}`);
            content.classList.toggle('show');
        }}

        function filterCards() {{
            const categoryFilter = document.getElementById('filter-category').value;
            const ratedFilter = document.getElementById('filter-rated').value;

            document.querySelectorAll('.query-card').forEach(card => {{
                const category = card.dataset.category;
                const isRated = card.classList.contains('rated');

                let show = true;

                if (categoryFilter && category !== categoryFilter) {{
                    show = false;
                }}

                if (ratedFilter === 'rated' && !isRated) {{
                    show = false;
                }}
                if (ratedFilter === 'unrated' && isRated) {{
                    show = false;
                }}

                card.classList.toggle('hidden', !show);
            }});
        }}

        function collectResults() {{
            const data = [];
            document.querySelectorAll('.query-card').forEach(card => {{
                const queryId = parseInt(card.dataset.queryId);
                const result = results.find(r => r.query_id === queryId);
                const ratings = propertyRatings[queryId] || {{}};

                // Count relevant in top 5 only for Precision@5
                let relevantInTop5 = 0;
                let totalRelevant = 0;
                let firstRelevantRank = 0;
                for (let i = 1; i <= 10; i++) {{
                    const rating = ratings[String(i)];
                    if (rating === 'relevant') {{
                        totalRelevant++;
                        if (firstRelevantRank === 0) {{
                            firstRelevantRank = i;
                        }}
                        if (i <= 5) {{
                            relevantInTop5++;
                        }}
                    }}
                }}

                const resultsCount = result.results_count || 0;
                const denominator = Math.min(resultsCount, 5);

                // Calculate overall precision
                let overallPrecision = '';
                if (resultsCount > 0) {{
                    overallPrecision = (totalRelevant / resultsCount).toFixed(4);
                }}

                // Calculate precision@5
                let precisionAt5 = '';
                if (denominator > 0) {{
                    const numerator = Math.min(relevantInTop5, denominator);
                    precisionAt5 = (numerator / denominator).toFixed(4);
                }}

                // Calculate MRR
                let mrr = '';
                if (resultsCount > 0) {{
                    mrr = firstRelevantRank > 0 ? (1 / firstRelevantRank).toFixed(4) : '0';
                }}

                // Calculate Success (binary: 1 if any relevant, 0 otherwise)
                const success = totalRelevant >= 1 ? 1 : 0;

                const qualitySelect = card.querySelector('.quality-rating');
                const notesInput = card.querySelector('.notes-input');

                data.push({{
                    query_id: queryId,
                    question: result.question,
                    category: result.category,
                    results_count: resultsCount,
                    relevant_count: totalRelevant,
                    relevant_in_top5: relevantInTop5,
                    first_relevant_rank: firstRelevantRank || '',
                    overall_precision: overallPrecision,
                    precision_at_5: precisionAt5,
                    mrr: mrr,
                    success: success,
                    response_quality: qualitySelect ? qualitySelect.value : '',
                    notes: notesInput ? notesInput.value : ''
                }});
            }});
            return data;
        }}

        function exportResults() {{
            const data = collectResults();

            const headers = ['query_id', 'question', 'category', 'results_count', 'relevant_count', 'relevant_in_top5', 'first_relevant_rank', 'overall_precision', 'precision_at_5', 'mrr', 'success', 'response_quality', 'notes'];
            let csv = headers.join(',') + '\\n';

            data.forEach(row => {{
                const values = headers.map(h => {{
                    let val = row[h] ?? '';
                    val = String(val).replace(/"/g, '""');
                    if (val.includes(',') || val.includes('"') || val.includes('\\n')) {{
                        val = '"' + val + '"';
                    }}
                    return val;
                }});
                csv += values.join(',') + '\\n';
            }});

            const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'evaluation_rated_{timestamp}.csv';
            link.click();

            alert('CSV exported! Run: python scripts/calculate_evaluation_metrics.py');
        }}

        function saveToLocalStorage() {{
            const data = {{
                propertyRatings: propertyRatings,
                formData: collectResults()
            }};
            localStorage.setItem('rag_evaluation_{timestamp}', JSON.stringify(data));
            alert('Progress saved!');
        }}

        function loadFromLocalStorage() {{
            const saved = localStorage.getItem('rag_evaluation_{timestamp}');
            if (!saved) {{
                alert('No saved progress found.');
                return;
            }}

            const data = JSON.parse(saved);

            // Restore property ratings
            if (data.propertyRatings) {{
                Object.assign(propertyRatings, data.propertyRatings);

                // Update UI
                Object.entries(propertyRatings).forEach(([queryId, ratings]) => {{
                    Object.entries(ratings).forEach(([propNum, rating]) => {{
                        const key = `${{queryId}}_${{propNum}}`;
                        const item = document.querySelector(`[data-prop-key="${{key}}"]`);
                        if (item) {{
                            item.classList.remove('relevant', 'not-relevant');
                            item.classList.add(rating);
                            if (rating === 'relevant') {{
                                item.querySelector('.btn-relevant').classList.add('active');
                            }} else {{
                                item.querySelector('.btn-not-relevant').classList.add('active');
                            }}
                        }}
                    }});
                    updateQueryStats(queryId);
                }});
            }}

            // Restore form data
            if (data.formData) {{
                data.formData.forEach(row => {{
                    const card = document.querySelector(`[data-query-id="${{row.query_id}}"]`);
                    if (card) {{
                        const successSelect = card.querySelector('.success-rating');
                        const qualitySelect = card.querySelector('.quality-rating');
                        const notesInput = card.querySelector('.notes-input');

                        if (successSelect) successSelect.value = row.success || '';
                        if (qualitySelect) qualitySelect.value = row.response_quality || '';
                        if (notesInput) notesInput.value = row.notes || '';
                    }}
                }});
            }}

            updateGlobalStats();
            alert('Progress loaded!');
        }}

        // Auto-load on page load
        if (localStorage.getItem('rag_evaluation_{timestamp}')) {{
            loadFromLocalStorage();
        }}
    </script>
</body>
</html>
'''


def generate_property_html(props: List[Dict], query_id: int) -> str:
    """Generate HTML for property list with rating buttons."""
    if not props:
        return '<p style="color: #888; padding: 20px;">No properties found in response</p>'

    items = []
    for idx, prop in enumerate(props):
        num = prop['num']
        title = prop['title']
        url = prop['url']
        price = prop['price']
        location = prop['location']
        specs = prop.get('specs', [])
        prop_type = prop.get('prop_type', '')

        # Make title a link if URL exists
        if url:
            title_html = f'<a href="{url}" target="_blank" rel="noopener">{title} ↗</a>'
        else:
            title_html = title

        # Build specs HTML
        specs_html = ''
        if specs:
            specs_str = ', '.join(specs)
            specs_html = f'<div class="property-specs">🏠 {specs_str}</div>'

        # Property type badge (Primary, Secondary, Rent)
        type_html = ''
        if prop_type:
            type_class = f'type-{prop_type.lower()}'  # type-primary, type-secondary, type-rent
            type_html = f'<span class="prop-type-badge {type_class}">{prop_type}</span>'

        # Mark items beyond position 5 (not counted in P@5, but counted in Overall P)
        position = idx + 1
        beyond_badge = '<span class="beyond-badge">P@5 excluded</span>' if position > 5 else ''

        items.append(f'''
            <div class="property-item" data-prop-key="{query_id}_{num}">
                <div class="property-num">{num}</div>
                <div class="property-content">
                    <div class="property-title">{title_html} {type_html} {beyond_badge}</div>
                    <div class="property-info">
                        {f'<span>💰 {price}</span>' if price else ''}
                        {f'<span>📍 {location}</span>' if location else ''}
                    </div>
                    {specs_html}
                </div>
                <div class="property-actions">
                    <button class="btn-relevant" onclick="toggleRelevance({query_id}, '{num}', true)" title="Relevant">✓</button>
                    <button class="btn-not-relevant" onclick="toggleRelevance({query_id}, '{num}', false)" title="Not Relevant">✗</button>
                </div>
            </div>
        ''')

    return '<div class="property-list">' + '\n'.join(items) + '</div>'


def generate_card_html(result: dict) -> str:
    """Generate HTML for a single query card."""
    query_id = result.get('query_id', 0)
    question = result.get('question', '')
    category = result.get('category', 'unknown')
    response = result.get('response', '(no response)')
    results_count = result.get('results_count', 0) or 0

    results_class = 'has-results' if results_count > 0 else 'no-results'

    # Parse properties from response
    properties = parse_properties_from_response(response)
    properties_html = generate_property_html(properties, query_id)

    # Escape response for HTML
    response_escaped = response.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    return f'''
        <div class="query-card" data-query-id="{query_id}" data-category="{category}" data-results-count="{results_count}">
            <div class="query-header">
                <span class="query-id">#{query_id}</span>
                <span class="query-text">{question}</span>
                <div class="query-meta">
                    <span class="category-tag">{category}</span>
                    <span class="results-badge {results_class}">{results_count} results</span>
                </div>
            </div>
            <div class="query-body">
                {properties_html}

                <div class="rating-section">
                    <div class="rating-field">
                        <label>Relevant / Total</label>
                        <div class="value"><span class="relevant-count-display">0</span> / {results_count}</div>
                    </div>
                    <div class="rating-field">
                        <label>1st Relevant</label>
                        <div class="value first-relevant-display">-</div>
                    </div>
                    <div class="rating-field">
                        <label>Overall Precision</label>
                        <div class="value overall-precision-display">-</div>
                    </div>
                    <div class="rating-field">
                        <label>Precision@5</label>
                        <div class="value precision-display">-</div>
                    </div>
                    <div class="rating-field">
                        <label>MRR</label>
                        <div class="value mrr-display">-</div>
                    </div>
                    <div class="rating-field">
                        <label>Success (Auto)</label>
                        <div class="value success-display">-</div>
                    </div>
                    <div class="rating-field">
                        <label>Quality (0-5)</label>
                        <select class="quality-rating">
                            <option value="">-</option>
                            <option value="5">5 - Excellent</option>
                            <option value="4">4 - Good</option>
                            <option value="3">3 - Fair</option>
                            <option value="2">2 - Poor</option>
                            <option value="1">1 - Bad</option>
                            <option value="0">0 - No results</option>
                        </select>
                    </div>
                    <div class="rating-field">
                        <label>Notes</label>
                        <textarea class="notes-input" placeholder="Optional..."></textarea>
                    </div>
                </div>

                <div class="raw-response">
                    <button class="raw-toggle" onclick="toggleRawResponse({query_id})">
                        📄 Show Raw Response
                    </button>
                    <div class="raw-content" id="raw-{query_id}">{response_escaped}</div>
                </div>
            </div>
        </div>
    '''


def generate_html(input_file: Path, output_file: Path):
    """Generate HTML evaluation interface."""

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data.get('results', [])
    timestamp = data.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))

    cards_html = '\n'.join(generate_card_html(r) for r in results)

    categories = sorted(set(r.get('category', 'unknown') for r in results))
    category_options = '\n'.join(f'<option value="{c}">{c}</option>' for c in categories)

    html = HTML_TEMPLATE.format(
        timestamp=timestamp,
        total_queries=len(results),
        cards_html=cards_html,
        category_options=category_options,
        results_json=json.dumps(results, ensure_ascii=False),
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_file


def main():
    parser = argparse.ArgumentParser(description='Generate HTML evaluation interface')
    parser.add_argument('--input', type=str, default=None, help='Input JSON file')
    parser.add_argument('--method', type=str, default='hybrid',
                        choices=['hybrid', 'api_only', 'vector_only'],
                        help='Search method (for finding latest results)')
    args = parser.parse_args()

    base_eval_dir = project_root / 'data' / 'evaluation'

    if args.input:
        input_file = Path(args.input)
        # Try to detect method from file path or content
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        method = data.get('search_method', args.method)
    else:
        # Look in new folder structure first: method/latest/test_results.json
        latest_dir = base_eval_dir / args.method / 'latest'
        input_file = latest_dir / 'test_results.json'
        if not input_file.exists():
            # Fallback to old structure
            method_dir = base_eval_dir / args.method
            input_file = method_dir / 'test_results_latest.json'
            if not input_file.exists():
                input_file = base_eval_dir / f'test_results_{args.method}_latest.json'
        method = args.method

    if not input_file.exists():
        print(f'[ERR] Input file not found: {input_file}')
        print(f'Run the test first: python scripts/test_sequential_chat.py --method {args.method}')
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    timestamp = data.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
    method = data.get('search_method', method)

    # Save to timestamped folder (new structure)
    eval_dir = base_eval_dir / method / timestamp
    eval_dir.mkdir(parents=True, exist_ok=True)

    output_file = eval_dir / 'evaluation.html'

    generate_html(input_file, output_file)

    print(f'[OK] HTML evaluation interface created: {output_file}')
    print(f'Method: {method.upper()}')
    print(f'Folder: {eval_dir}')
    print(f'\nFeatures:')
    print(f'  - Click checkmark or X on each property to rate relevance')
    print(f'  - Click property title to open detail page (new tab)')
    print(f'  - Auto-calculates Precision@5')
    print(f'  - Progress auto-saved to localStorage')


if __name__ == '__main__':
    main()
