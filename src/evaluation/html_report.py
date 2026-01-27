"""
HTML report generator for evaluation results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import (
    ConstraintResult,
    QueryEvaluation,
    EvaluationMetrics,
    PropertyCheck,
)


class HTMLReportGenerator:
    """
    Generate detailed HTML reports for evaluation results.
    """

    def __init__(self):
        self.css = self._get_css()
        self.js = self._get_js()

    def _get_css(self) -> str:
        return """
        :root {
            --primary: #2563eb;
            --success: #16a34a;
            --danger: #dc2626;
            --warning: #ca8a04;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-500: #6b7280;
            --gray-700: #374151;
            --gray-900: #111827;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--gray-100);
            color: var(--gray-900);
            line-height: 1.5;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: white;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 1.5rem;
            margin-bottom: 8px;
        }

        .meta {
            color: var(--gray-500);
            font-size: 14px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }

        .stat-label {
            font-size: 13px;
            color: var(--gray-500);
            margin-top: 4px;
        }

        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 16px;
            overflow: hidden;
        }

        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-header h2 {
            font-size: 1.1rem;
        }

        .card-body {
            padding: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--gray-200);
        }

        th {
            font-weight: 600;
            background: var(--gray-50);
        }

        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-pass {
            background: #dcfce7;
            color: var(--success);
        }

        .badge-fail {
            background: #fef2f2;
            color: var(--danger);
        }

        .badge-na {
            background: var(--gray-100);
            color: var(--gray-500);
        }

        .badge-missing {
            background: #fef9c3;
            color: var(--warning);
        }

        .badge-success {
            background: #dcfce7;
            color: var(--success);
        }

        .badge-warning {
            background: #fef9c3;
            color: var(--warning);
        }

        .badge-category {
            background: #e0e7ff;
            color: #4f46e5;
        }

        .query-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
        }

        .query-header {
            padding: 12px 16px;
            background: var(--gray-50);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .query-header:hover {
            background: var(--gray-100);
        }

        .query-id {
            font-weight: 600;
            color: var(--primary);
            margin-right: 12px;
        }

        .query-text {
            flex: 1;
        }

        .query-meta {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .query-body {
            display: none;
            padding: 16px;
            border-top: 1px solid var(--gray-200);
        }

        .query-body.expanded {
            display: block;
        }

        .cpr-bar {
            width: 100px;
            height: 8px;
            background: var(--gray-200);
            border-radius: 4px;
            overflow: hidden;
        }

        .cpr-fill {
            height: 100%;
            background: var(--success);
            transition: width 0.3s;
        }

        .cpr-fill.low {
            background: var(--danger);
        }

        .cpr-fill.medium {
            background: var(--warning);
        }

        .cm-grid {
            display: grid;
            grid-template-columns: repeat(2, 100px);
            gap: 8px;
            margin: 16px 0;
        }

        .cm-cell {
            padding: 16px;
            text-align: center;
            border-radius: 4px;
            font-weight: 600;
        }

        .cm-tp { background: #dcfce7; color: var(--success); }
        .cm-fp { background: #fef2f2; color: var(--danger); }
        .cm-tn { background: #e0f2fe; color: #0369a1; }
        .cm-fn { background: #fef9c3; color: var(--warning); }

        .pca-chart {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .pca-row {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .pca-label {
            width: 100px;
            font-size: 13px;
        }

        .pca-bar {
            flex: 1;
            height: 24px;
            background: var(--gray-200);
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }

        .pca-fill {
            height: 100%;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            color: white;
            font-size: 12px;
            font-weight: 500;
        }

        .filter-controls {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }

        .filter-btn {
            padding: 6px 12px;
            border: 1px solid var(--gray-300);
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }

        .filter-btn.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        .hidden {
            display: none !important;
        }

        /* Manual Review Controls */
        .review-controls {
            background: #fffbeb;
            border: 1px solid #fbbf24;
            border-radius: 6px;
            padding: 12px;
            margin-top: 12px;
        }

        .review-controls label {
            font-size: 13px;
            font-weight: 500;
            margin-right: 8px;
        }

        .review-controls select {
            padding: 4px 8px;
            border: 1px solid var(--gray-300);
            border-radius: 4px;
            font-size: 13px;
        }

        .review-controls input[type="text"] {
            padding: 4px 8px;
            border: 1px solid var(--gray-300);
            border-radius: 4px;
            font-size: 13px;
            width: 300px;
            margin-left: 12px;
        }

        .review-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 500;
            margin-left: 8px;
        }

        .review-badge.override-pass {
            background: #dcfce7;
            color: var(--success);
        }

        .review-badge.override-fail {
            background: #fef2f2;
            color: var(--danger);
        }

        .save-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 8px;
        }

        .save-btn:hover {
            background: #1d4ed8;
        }

        .recalc-btn {
            background: var(--success);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .recalc-btn:hover {
            background: #15803d;
        }

        .review-summary {
            background: #fef3c7;
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 12px;
            font-size: 13px;
        }

        /* Detail modal styles */
        .property-detail {
            background: var(--gray-50);
            border: 1px solid var(--gray-200);
            border-radius: 6px;
            margin: 8px 0;
            overflow: hidden;
        }

        .property-detail-header {
            padding: 10px 14px;
            background: white;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
        }

        .property-detail-header:hover {
            background: var(--gray-50);
        }

        .property-detail-body {
            display: none;
            padding: 14px;
            border-top: 1px solid var(--gray-200);
        }

        .property-detail-body.expanded {
            display: block;
        }

        .detail-grid {
            display: grid;
            grid-template-columns: 120px 1fr 1fr 1fr 80px;
            gap: 8px;
            font-size: 13px;
        }

        .detail-grid-header {
            font-weight: 600;
            color: var(--gray-700);
            padding: 6px 0;
            border-bottom: 1px solid var(--gray-200);
        }

        .detail-row {
            display: contents;
        }

        .detail-row > div {
            padding: 6px 4px;
            border-bottom: 1px solid var(--gray-100);
        }

        .detail-label {
            font-weight: 500;
            color: var(--gray-600);
        }

        .detail-value {
            font-family: monospace;
            font-size: 12px;
        }

        .detail-match {
            color: var(--success);
        }

        .detail-mismatch {
            color: var(--danger);
        }

        .gold-constraint {
            background: #fef3c7;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }

        .api-value {
            background: #dbeafe;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }

        .extracted-value {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }

        /* Clickable constraint badges */
        .badge-clickable {
            cursor: pointer;
            user-select: none;
            transition: all 0.15s ease;
        }

        .badge-clickable:hover {
            transform: scale(1.1);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .badge-override {
            border: 2px solid #7c3aed !important;
            font-weight: 700;
        }

        .cpr-value {
            font-weight: 600;
            font-size: 13px;
        }

        .cpr-value.cpr-pass {
            color: var(--success);
        }

        .cpr-value.cpr-fail {
            color: var(--danger);
        }

        .constraint-cell {
            text-align: center;
        }

        /* Manual Evaluation Cards */
        .manual-eval-card {
            background: white;
            border: 2px solid #f59e0b;
            border-radius: 8px;
            margin: 12px 0;
            overflow: hidden;
        }

        .manual-eval-header {
            background: #fffbeb;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #fde68a;
        }

        .manual-eval-body {
            padding: 16px;
        }

        .property-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }

        .property-info-section {
            background: var(--gray-50);
            padding: 12px;
            border-radius: 6px;
        }

        .property-info-section h4 {
            font-size: 12px;
            color: var(--gray-500);
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .property-specs {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .spec-badge {
            background: #e0f2fe;
            color: #0369a1;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .property-url {
            display: block;
            color: var(--primary);
            font-size: 13px;
            word-break: break-all;
            margin-top: 8px;
        }

        .property-description {
            font-size: 13px;
            color: var(--gray-700);
            line-height: 1.6;
            max-height: 100px;
            overflow-y: auto;
        }

        .google-map-container {
            width: 100%;
            height: 200px;
            border-radius: 6px;
            overflow: hidden;
            margin-top: 12px;
        }

        .google-map-container iframe {
            width: 100%;
            height: 100%;
            border: 0;
        }

        .manual-eval-controls {
            background: #fef3c7;
            border: 1px solid #fbbf24;
            border-radius: 6px;
            padding: 16px;
            margin-top: 16px;
        }

        .manual-eval-buttons {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }

        .eval-btn {
            padding: 10px 24px;
            border: 2px solid;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .eval-btn-pass {
            border-color: var(--success);
            color: var(--success);
            background: white;
        }

        .eval-btn-pass:hover, .eval-btn-pass.selected {
            background: var(--success);
            color: white;
        }

        .eval-btn-fail {
            border-color: var(--danger);
            color: var(--danger);
            background: white;
        }

        .eval-btn-fail:hover, .eval-btn-fail.selected {
            background: var(--danger);
            color: white;
        }

        .eval-comment {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--gray-300);
            border-radius: 4px;
            font-size: 13px;
            resize: vertical;
            min-height: 60px;
        }

        .manual-pending {
            background: #fef3c7;
            color: #92400e;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }

        .manual-pass {
            background: #dcfce7;
            color: var(--success);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }

        .manual-fail {
            background: #fef2f2;
            color: var(--danger);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        """

    def _get_js(self) -> str:
        return """
        function toggleQuery(idx) {
            const body = document.getElementById('query-body-' + idx);
            body.classList.toggle('expanded');
        }

        function togglePropertyDetail(queryIdx, propIdx) {
            const body = document.getElementById('prop-detail-' + queryIdx + '-' + propIdx);
            body.classList.toggle('expanded');
        }

        function filterQueries(filter) {
            const cards = document.querySelectorAll('.query-card');
            const btns = document.querySelectorAll('.filter-btn');

            btns.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            cards.forEach(card => {
                if (filter === 'all') {
                    card.classList.remove('hidden');
                } else if (filter === 'failed') {
                    const success = card.dataset.success === 'true';
                    card.classList.toggle('hidden', success);
                } else if (filter === 'passed') {
                    const success = card.dataset.success === 'true';
                    card.classList.toggle('hidden', !success);
                }
            });
        }

        function exportJSON() {
            const data = window.evaluationData;
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'evaluation_results.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        // ============================================================
        // Manual Review - Per-Constraint Override System
        // ============================================================

        // Structure: {queryId: {propIdx: {constraint: 'pass'|'fail'|'na'}}}
        window.constraintOverrides = {};

        // Original data for recalculation
        window.originalData = {};

        function toggleConstraint(queryId, propIdx, constraint, currentResult) {
            // Initialize structure if needed
            if (!window.constraintOverrides[queryId]) {
                window.constraintOverrides[queryId] = {};
            }
            if (!window.constraintOverrides[queryId][propIdx]) {
                window.constraintOverrides[queryId][propIdx] = {};
            }

            // Cycle through: original -> pass -> fail -> na -> original
            const key = queryId + '-' + propIdx + '-' + constraint;
            const badge = document.getElementById('badge-' + key);
            const current = window.constraintOverrides[queryId][propIdx][constraint];

            let newValue;
            if (!current) {
                // First click: if currently pass, go to fail; if fail, go to pass
                newValue = (currentResult === 'pass') ? 'fail' : 'pass';
            } else if (current === 'pass') {
                newValue = 'fail';
            } else if (current === 'fail') {
                newValue = 'na';
            } else if (current === 'na') {
                // Reset to original
                delete window.constraintOverrides[queryId][propIdx][constraint];
                newValue = null;
            }

            if (newValue) {
                window.constraintOverrides[queryId][propIdx][constraint] = newValue;
            }

            // Update badge display
            updateBadgeDisplay(key, newValue, currentResult);

            // Recalculate CPR for this property
            recalculatePropertyCPR(queryId, propIdx);

            // Update summary
            updateOverrideSummary();
        }

        function updateBadgeDisplay(key, newValue, originalValue) {
            const badge = document.getElementById('badge-' + key);
            if (!badge) return;

            // Remove all badge classes
            badge.classList.remove('badge-pass', 'badge-fail', 'badge-na', 'badge-override');

            const displayValue = newValue || originalValue;
            badge.classList.add('badge-' + displayValue);

            if (newValue) {
                badge.classList.add('badge-override');
                badge.textContent = displayValue.toUpperCase() + ' *';
            } else {
                badge.textContent = originalValue.toUpperCase();
            }
        }

        function recalculatePropertyCPR(queryId, propIdx) {
            const propData = window.originalData[queryId]?.properties?.[propIdx];
            if (!propData) return;

            const overrides = window.constraintOverrides[queryId]?.[propIdx] || {};

            // Get constraint results (use override if exists, else original)
            const constraints = ['property_type', 'listing_type', 'location', 'price', 'bedrooms', 'floors'];
            let passCount = 0;
            let totalCount = 0;

            constraints.forEach(c => {
                const original = propData[c + '_result'];
                if (original === 'na') return; // Skip N/A constraints

                totalCount++;
                const value = overrides[c] || original;
                if (value === 'pass') passCount++;
            });

            const cpr = totalCount > 0 ? passCount / totalCount : 0;

            // Update CPR display
            const cprEl = document.getElementById('cpr-' + queryId + '-' + propIdx);
            if (cprEl) {
                const pct = Math.round(cpr * 100);
                cprEl.textContent = pct + '%';
                cprEl.className = cpr >= 0.6 ? 'cpr-value cpr-pass' : 'cpr-value cpr-fail';
            }

            // Update CPR bar
            const cprBar = document.getElementById('cpr-bar-' + queryId + '-' + propIdx);
            if (cprBar) {
                cprBar.style.width = Math.round(cpr * 100) + '%';
                cprBar.className = 'cpr-fill ' + (cpr < 0.4 ? 'low' : cpr < 0.6 ? 'medium' : '');
            }

            // Recalculate query-level metrics
            recalculateQueryMetrics(queryId);
        }

        function recalculateQueryMetrics(queryId) {
            const queryData = window.originalData[queryId];
            if (!queryData) return;

            let totalCPR = 0;
            let propCount = queryData.properties?.length || 0;

            for (let propIdx = 0; propIdx < propCount; propIdx++) {
                const propData = queryData.properties[propIdx];
                const overrides = window.constraintOverrides[queryId]?.[propIdx] || {};

                const constraints = ['property_type', 'listing_type', 'location', 'price', 'bedrooms', 'floors'];
                let passCount = 0;
                let totalCount = 0;

                constraints.forEach(c => {
                    const original = propData[c + '_result'];
                    if (original === 'na') return;
                    totalCount++;
                    const value = overrides[c] || original;
                    if (value === 'pass') passCount++;
                });

                totalCPR += totalCount > 0 ? passCount / totalCount : 0;
            }

            const meanCPR = propCount > 0 ? totalCPR / propCount : 0;

            // Update query-level CPR display
            const queryCard = document.querySelector('.query-card[data-query-id="' + queryId + '"]');
            if (queryCard) {
                const cprBar = queryCard.querySelector('.query-meta .cpr-bar .cpr-fill');
                if (cprBar) {
                    const pct = Math.round(meanCPR * 100);
                    cprBar.style.width = pct + '%';
                    cprBar.className = 'cpr-fill ' + (meanCPR < 0.4 ? 'low' : meanCPR < 0.6 ? 'medium' : '');
                }
            }
        }

        function updateOverrideSummary() {
            let totalOverrides = 0;
            Object.keys(window.constraintOverrides).forEach(qid => {
                Object.keys(window.constraintOverrides[qid]).forEach(pid => {
                    totalOverrides += Object.keys(window.constraintOverrides[qid][pid]).length;
                });
            });

            const summary = document.getElementById('review-summary');
            if (totalOverrides > 0) {
                summary.style.display = 'block';
                summary.innerHTML = '<strong>' + totalOverrides + '</strong> constraint override(s). ' +
                    '<button class="filter-btn" onclick="clearAllOverrides()" style="margin-left: 10px;">Clear All</button>';
            } else {
                summary.style.display = 'none';
            }
        }

        function clearAllOverrides() {
            if (!confirm('Clear all overrides?')) return;

            // Reset all badges to original
            Object.keys(window.constraintOverrides).forEach(qid => {
                Object.keys(window.constraintOverrides[qid]).forEach(pid => {
                    Object.keys(window.constraintOverrides[qid][pid]).forEach(constraint => {
                        const key = qid + '-' + pid + '-' + constraint;
                        const original = window.originalData[qid]?.properties?.[pid]?.[constraint + '_result'] || 'na';
                        updateBadgeDisplay(key, null, original);
                    });
                });
            });

            window.constraintOverrides = {};

            // Recalculate all
            Object.keys(window.originalData).forEach(qid => {
                recalculateQueryMetrics(qid);
            });

            updateOverrideSummary();
        }

        function saveOverrides() {
            const data = {
                timestamp: new Date().toISOString(),
                constraint_overrides: window.constraintOverrides
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'evaluation_overrides.json';
            a.click();
            URL.revokeObjectURL(url);

            let count = 0;
            Object.values(window.constraintOverrides).forEach(q => {
                Object.values(q).forEach(p => {
                    count += Object.keys(p).length;
                });
            });
            alert('Saved ' + count + ' constraint overrides.');
        }

        function recalculateMetrics() {
            // Calculate new metrics based on overrides
            let totalQueries = Object.keys(window.originalData).length;
            let successQueries = 0;
            let totalProperties = 0;
            let totalCPR = 0;
            let strictPass = 0;

            // Per-constraint accuracy
            const pca = {
                property_type: {pass: 0, total: 0},
                listing_type: {pass: 0, total: 0},
                location: {pass: 0, total: 0},
                price: {pass: 0, total: 0},
                bedrooms: {pass: 0, total: 0},
                floors: {pass: 0, total: 0}
            };

            Object.keys(window.originalData).forEach(qid => {
                const queryData = window.originalData[qid];
                let queryTotalCPR = 0;
                let propCount = queryData.properties?.length || 0;
                totalProperties += propCount;

                for (let propIdx = 0; propIdx < propCount; propIdx++) {
                    const propData = queryData.properties[propIdx];
                    const overrides = window.constraintOverrides[qid]?.[propIdx] || {};

                    let passCount = 0;
                    let totalCount = 0;

                    ['property_type', 'listing_type', 'location', 'price', 'bedrooms', 'floors'].forEach(c => {
                        const original = propData[c + '_result'];
                        if (original === 'na') return;

                        totalCount++;
                        pca[c].total++;

                        const value = overrides[c] || original;
                        if (value === 'pass') {
                            passCount++;
                            pca[c].pass++;
                        }
                    });

                    const propCPR = totalCount > 0 ? passCount / totalCount : 0;
                    queryTotalCPR += propCPR;
                    totalCPR += propCPR;

                    if (propCPR === 1.0) strictPass++;
                }

                const meanQueryCPR = propCount > 0 ? queryTotalCPR / propCount : 0;
                if (meanQueryCPR >= 0.6) successQueries++;
            });

            // Display new metrics
            const meanCPR = totalProperties > 0 ? totalCPR / totalProperties : 0;
            const successRate = totalQueries > 0 ? successQueries / totalQueries : 0;
            const strictRate = totalProperties > 0 ? strictPass / totalProperties : 0;

            let pcaSummary = '';
            Object.keys(pca).forEach(c => {
                if (pca[c].total > 0) {
                    const rate = (pca[c].pass / pca[c].total * 100).toFixed(1);
                    pcaSummary += c.replace('_', ' ') + ': ' + rate + '% | ';
                }
            });

            alert('Recalculated Metrics:\\n\\n' +
                  'Query Success Rate: ' + (successRate * 100).toFixed(1) + '%\\n' +
                  'Mean CPR: ' + (meanCPR * 100).toFixed(1) + '%\\n' +
                  'Strict Success: ' + (strictRate * 100).toFixed(1) + '%\\n\\n' +
                  'PCA:\\n' + pcaSummary);
        }

        // ============================================================
        // Manual Evaluation Functions (for Q22-30)
        // ============================================================

        // Structure: {queryId: {propIdx: {result: 'pass'|'fail'|null, comment: ''}}}
        window.manualEvaluations = {};

        function setManualResult(queryId, propIdx, result) {
            if (!window.manualEvaluations[queryId]) {
                window.manualEvaluations[queryId] = {};
            }
            if (!window.manualEvaluations[queryId][propIdx]) {
                window.manualEvaluations[queryId][propIdx] = {result: null, comment: ''};
            }

            window.manualEvaluations[queryId][propIdx].result = result;

            // Update button styles
            const passBtn = document.getElementById('manual-pass-' + queryId + '-' + propIdx);
            const failBtn = document.getElementById('manual-fail-' + queryId + '-' + propIdx);

            passBtn.classList.toggle('selected', result === 'pass');
            failBtn.classList.toggle('selected', result === 'fail');

            // Update status badge
            const statusBadge = document.getElementById('manual-status-' + queryId + '-' + propIdx);
            if (result === 'pass') {
                statusBadge.className = 'manual-pass';
                statusBadge.textContent = 'PASS';
            } else if (result === 'fail') {
                statusBadge.className = 'manual-fail';
                statusBadge.textContent = 'FAIL';
            } else {
                statusBadge.className = 'manual-pending';
                statusBadge.textContent = 'PENDING';
            }

            // Update CPR display
            updateManualCPR(queryId, propIdx, result);

            // Recalculate query metrics
            recalculateManualQueryMetrics(queryId);

            console.log('Manual eval:', queryId, propIdx, result);
        }

        function setManualComment(queryId, propIdx, comment) {
            if (!window.manualEvaluations[queryId]) {
                window.manualEvaluations[queryId] = {};
            }
            if (!window.manualEvaluations[queryId][propIdx]) {
                window.manualEvaluations[queryId][propIdx] = {result: null, comment: ''};
            }
            window.manualEvaluations[queryId][propIdx].comment = comment;
        }

        function updateManualCPR(queryId, propIdx, result) {
            const cprEl = document.getElementById('manual-cpr-' + queryId + '-' + propIdx);
            if (cprEl) {
                if (result === 'pass') {
                    cprEl.textContent = '100%';
                    cprEl.className = 'cpr-value cpr-pass';
                } else if (result === 'fail') {
                    cprEl.textContent = '0%';
                    cprEl.className = 'cpr-value cpr-fail';
                } else {
                    cprEl.textContent = 'Pending';
                    cprEl.className = 'cpr-value';
                }
            }
        }

        function recalculateManualQueryMetrics(queryId) {
            const evals = window.manualEvaluations[queryId] || {};
            const queryData = window.originalData[queryId];
            if (!queryData) return;

            let totalCPR = 0;
            let propCount = queryData.properties?.length || 0;
            let evaluatedCount = 0;

            for (let propIdx = 0; propIdx < propCount; propIdx++) {
                const manualResult = evals[propIdx]?.result;
                if (manualResult === 'pass') {
                    totalCPR += 1;
                    evaluatedCount++;
                } else if (manualResult === 'fail') {
                    evaluatedCount++;
                }
            }

            const meanCPR = evaluatedCount > 0 ? totalCPR / evaluatedCount : 0;

            // Update query-level display
            const queryCard = document.querySelector('.query-card[data-query-id="' + queryId + '"]');
            if (queryCard) {
                const cprBar = queryCard.querySelector('.query-meta .cpr-bar .cpr-fill');
                if (cprBar) {
                    const pct = Math.round(meanCPR * 100);
                    cprBar.style.width = pct + '%';
                    cprBar.className = 'cpr-fill ' + (meanCPR < 0.4 ? 'low' : meanCPR < 0.6 ? 'medium' : '');
                }
            }
        }

        function saveManualEvaluations() {
            const data = {
                timestamp: new Date().toISOString(),
                manual_evaluations: window.manualEvaluations
            };
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'manual_evaluations.json';
            a.click();
            URL.revokeObjectURL(url);

            let count = 0;
            Object.values(window.manualEvaluations).forEach(q => {
                Object.values(q).forEach(p => {
                    if (p.result) count++;
                });
            });
            alert('Saved ' + count + ' manual evaluations.');
        }

        // ============================================================
        // Save All Evaluations (Constraint Overrides + Manual Evals)
        // ============================================================
        function saveAllEvaluations() {
            // Count overrides
            let overrideCount = 0;
            Object.values(window.constraintOverrides).forEach(q => {
                Object.values(q).forEach(p => {
                    overrideCount += Object.keys(p).length;
                });
            });

            // Count manual evaluations
            let manualCount = 0;
            Object.values(window.manualEvaluations).forEach(q => {
                Object.values(q).forEach(p => {
                    if (p.result) manualCount++;
                });
            });

            if (overrideCount === 0 && manualCount === 0) {
                alert('No evaluations to save. Please evaluate some properties first.');
                return;
            }

            const data = {
                timestamp: new Date().toISOString(),
                source_report: window.location.pathname.split('/').pop().replace('.html', ''),
                summary: {
                    constraint_overrides_count: overrideCount,
                    manual_evaluations_count: manualCount
                },
                constraint_overrides: window.constraintOverrides,
                manual_evaluations: window.manualEvaluations
            };

            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'manual_input.json';
            a.click();
            URL.revokeObjectURL(url);

            const sourceReport = data.source_report || 'evaluation';
            alert('Saved all evaluations!\\n\\n' +
                  '- Constraint overrides (Q1-21): ' + overrideCount + '\\n' +
                  '- Manual evaluations (Q22-30): ' + manualCount + '\\n\\n' +
                  'File downloaded: manual_input.json\\n\\n' +
                  'To regenerate report with final metrics:\\n\\n' +
                  'python scripts/evaluate_v2.py \\\\\\n' +
                  '  --results data/evaluation/v2/' + sourceReport + '/results.json \\\\\\n' +
                  '  --manual-input manual_input.json \\\\\\n' +
                  '  --output data/evaluation/v2/' + sourceReport + '_final');
        }

        function recalculateAllMetrics() {
            // Combine auto and manual evaluations
            let totalQueries = Object.keys(window.originalData).length;
            let successQueries = 0;
            let totalProperties = 0;
            let totalCPR = 0;
            let strictPass = 0;

            Object.keys(window.originalData).forEach(qid => {
                const queryData = window.originalData[qid];
                const isManual = queryData.is_manual_evaluation;
                let queryTotalCPR = 0;
                let propCount = queryData.properties?.length || 0;
                totalProperties += propCount;

                for (let propIdx = 0; propIdx < propCount; propIdx++) {
                    let propCPR;

                    if (isManual) {
                        const manualResult = window.manualEvaluations[qid]?.[propIdx]?.result;
                        propCPR = manualResult === 'pass' ? 1.0 : 0.0;
                    } else {
                        const propData = queryData.properties[propIdx];
                        const overrides = window.constraintOverrides[qid]?.[propIdx] || {};

                        let passCount = 0;
                        let totalCount = 0;

                        ['property_type', 'listing_type', 'location', 'price', 'bedrooms', 'floors'].forEach(c => {
                            const original = propData[c + '_result'];
                            if (original === 'na') return;

                            totalCount++;
                            const value = overrides[c] || original;
                            if (value === 'pass') passCount++;
                        });

                        propCPR = totalCount > 0 ? passCount / totalCount : 0;
                    }

                    queryTotalCPR += propCPR;
                    totalCPR += propCPR;
                    if (propCPR === 1.0) strictPass++;
                }

                const meanQueryCPR = propCount > 0 ? queryTotalCPR / propCount : 0;
                const hasResults = propCount > 0;
                const expectedHasData = queryData.expected_result === 'has_data';

                if (expectedHasData) {
                    if (hasResults && meanQueryCPR >= 0.6) successQueries++;
                } else {
                    if (!hasResults) successQueries++;
                }
            });

            const meanCPR = totalProperties > 0 ? totalCPR / totalProperties : 0;
            const successRate = totalQueries > 0 ? successQueries / totalQueries : 0;
            const strictRate = totalProperties > 0 ? strictPass / totalProperties : 0;

            alert('Recalculated Metrics (Auto + Manual):\\n\\n' +
                  'Query Success Rate: ' + (successRate * 100).toFixed(1) + '%\\n' +
                  'Mean CPR: ' + (meanCPR * 100).toFixed(1) + '%\\n' +
                  'Strict Success: ' + (strictRate * 100).toFixed(1) + '%');
        }
        """

    def _result_badge(self, result: ConstraintResult, clickable: bool = False, badge_id: str = None, constraint: str = None) -> str:
        """Generate HTML badge for constraint result."""
        result_str = result.value if hasattr(result, 'value') else str(result).lower()

        badge_class = {
            ConstraintResult.PASS: 'badge-pass',
            ConstraintResult.FAIL: 'badge-fail',
            ConstraintResult.NA: 'badge-na',
            ConstraintResult.MISSING: 'badge-missing',
        }.get(result, 'badge-na')

        text = {
            ConstraintResult.PASS: 'PASS',
            ConstraintResult.FAIL: 'FAIL',
            ConstraintResult.NA: 'N/A',
            ConstraintResult.MISSING: 'MISSING',
        }.get(result, '?')

        if clickable and badge_id and constraint:
            return f'<span id="badge-{badge_id}" class="badge {badge_class} badge-clickable" onclick="toggleConstraint({badge_id.split("-")[0]}, {badge_id.split("-")[1]}, \'{constraint}\', \'{result_str}\')" title="Click to override">{text}</span>'
        else:
            return f'<span class="badge {badge_class}">{text}</span>'

    def _cpr_bar(self, cpr: float) -> str:
        """Generate CPR progress bar HTML."""
        pct = int(cpr * 100)
        css_class = ""
        if cpr < 0.4:
            css_class = "low"
        elif cpr < 0.6:
            css_class = "medium"
        return f'''
        <div class="cpr-bar">
            <div class="cpr-fill {css_class}" style="width: {pct}%"></div>
        </div>
        <span style="font-size: 12px; margin-left: 4px;">{pct}%</span>
        '''

    def _format_price(self, price) -> str:
        """Format price for display."""
        if price is None:
            return "N/A"
        try:
            return f"Rp {int(price):,}"
        except (ValueError, TypeError):
            return str(price)

    def _property_detail_card(
        self,
        query_idx: int,
        prop_idx: int,
        check: PropertyCheck,
        raw_prop: dict,
        gold_constraints: dict,
        query_id: int = None,
    ) -> str:
        """Generate detailed property card with constraint breakdown."""
        api_data = raw_prop.get("api_data", {})
        verified = raw_prop.get("verified", False)

        # Use query_id for JavaScript (fallback to query_idx)
        qid = query_id if query_id is not None else query_idx

        # Build constraint detail rows with clickable badges
        def make_row(label, extracted, gold, api_val, result, constraint_name):
            badge_id = f"{qid}-{prop_idx}-{constraint_name}"
            result_badge = self._result_badge(result, clickable=True, badge_id=badge_id, constraint=constraint_name)
            match_class = "detail-match" if result == ConstraintResult.PASS else "detail-mismatch" if result == ConstraintResult.FAIL else ""
            return f'''
            <div class="detail-row">
                <div class="detail-label">{label}</div>
                <div class="detail-value"><span class="extracted-value">{extracted}</span></div>
                <div class="detail-value"><span class="gold-constraint">{gold}</span></div>
                <div class="detail-value"><span class="api-value">{api_val}</span></div>
                <div class="constraint-cell {match_class}">{result_badge}</div>
            </div>
            '''

        # Property Type
        gold_type = gold_constraints.get("property_type", "N/A")
        extracted_type = raw_prop.get("property_type", "N/A")
        api_type = api_data.get("property_type", "N/A") if verified else "?"
        type_row = make_row("Property Type", extracted_type, gold_type, api_type, check.property_type_result, "property_type")

        # Listing Type
        gold_listing = gold_constraints.get("listing_type", "N/A")
        extracted_listing = raw_prop.get("listing_type", "N/A")
        api_listing = api_data.get("listing_type", "N/A") if verified else "?"
        listing_row = make_row("Listing Type", extracted_listing, gold_listing, api_listing, check.listing_type_result, "listing_type")

        # Location
        loc_constraint = gold_constraints.get("location", {})
        gold_loc = ", ".join(loc_constraint.get("keywords", [])) if loc_constraint else "N/A"
        extracted_loc = raw_prop.get("location", "N/A")
        if extracted_loc and len(str(extracted_loc)) > 40:
            extracted_loc = str(extracted_loc)[:40] + "..."
        api_loc = api_data.get("location", "N/A") if verified else "?"
        if api_loc and len(str(api_loc)) > 40:
            api_loc = str(api_loc)[:40] + "..."

        # Calculate distance - use from check, or calculate from API data if available
        distance_km = check.location_distance_km
        if distance_km is None and verified and loc_constraint:
            # Try to calculate distance from API coordinates
            api_lat = api_data.get("latitude")
            api_lng = api_data.get("longitude")
            gold_lat = loc_constraint.get("lat")
            gold_lng = loc_constraint.get("lng")
            if api_lat and api_lng and gold_lat and gold_lng:
                try:
                    from src.evaluation.constraint_checker import ConstraintChecker
                    distance_km = ConstraintChecker().haversine_distance(
                        float(api_lat), float(api_lng), float(gold_lat), float(gold_lng)
                    )
                except Exception:
                    pass

        # Build location note with all available info
        loc_notes = []
        if check.location_keyword_match:
            loc_notes.append(f"matched: {check.location_keyword_match}")
        if distance_km is not None:
            radius = loc_constraint.get("radius_km") if loc_constraint else None
            if radius is not None:
                status = "OK" if distance_km <= float(radius) else "TOO FAR"
                loc_notes.append(f"<strong>{distance_km:.1f}km</strong> (radius: {radius}km) [{status}]")
            else:
                loc_notes.append(f"<strong>{distance_km:.1f}km</strong>")
        loc_note = f" ({', '.join(loc_notes)})" if loc_notes else ""

        # Add failure reason if location check failed
        location_extra = ""
        if check.location_result == ConstraintResult.FAIL and check.location_failure_reason:
            location_extra = f'<br><small style="color: #dc2626; font-style: italic;">Reason: {check.location_failure_reason}</small>'

        location_row = make_row(f"Location{loc_note}", extracted_loc or "N/A", gold_loc, api_loc + location_extra or "N/A", check.location_result, "location")

        # Price
        price_constraint = gold_constraints.get("price", {})
        gold_price_parts = []
        if price_constraint.get("target"):
            tolerance = price_constraint.get("tolerance", 0.0)
            target = price_constraint["target"]
            min_p = target * (1 - tolerance)
            max_p = target * (1 + tolerance)
            gold_price_parts.append(f"~{self._format_price(target)} (±{int(tolerance*100)}%: {self._format_price(min_p)}-{self._format_price(max_p)})")
        else:
            if price_constraint.get("min"):
                gold_price_parts.append(f"min: {self._format_price(price_constraint['min'])}")
            if price_constraint.get("max"):
                gold_price_parts.append(f"max: {self._format_price(price_constraint['max'])}")
        gold_price = ", ".join(gold_price_parts) if gold_price_parts else "N/A"
        extracted_price = self._format_price(raw_prop.get("price"))
        api_price = self._format_price(api_data.get("price")) if verified else "?"
        price_row = make_row("Price", extracted_price, gold_price, api_price, check.price_result, "price")

        # Bedrooms
        bed_constraint = gold_constraints.get("bedrooms", {})
        gold_bed_parts = []
        if bed_constraint.get("min"):
            gold_bed_parts.append(f"min: {bed_constraint['min']}")
        if bed_constraint.get("max"):
            gold_bed_parts.append(f"max: {bed_constraint['max']}")
        if bed_constraint.get("exact"):
            gold_bed_parts.append(f"exact: {bed_constraint['exact']}")
        gold_bed = ", ".join(gold_bed_parts) if gold_bed_parts else "N/A"
        extracted_bed = str(raw_prop.get("bedrooms", "N/A"))
        api_bed = str(api_data.get("bedrooms", "N/A")) if verified else "?"
        bed_row = make_row("Bedrooms", extracted_bed, gold_bed, api_bed, check.bedrooms_result, "bedrooms")

        # Floors
        floors_constraint = gold_constraints.get("floors", {})
        gold_floors_parts = []
        if floors_constraint.get("min"):
            gold_floors_parts.append(f"min: {floors_constraint['min']}")
        if floors_constraint.get("max"):
            gold_floors_parts.append(f"max: {floors_constraint['max']}")
        if floors_constraint.get("exact"):
            gold_floors_parts.append(f"exact: {floors_constraint['exact']}")
        gold_floors = ", ".join(gold_floors_parts) if gold_floors_parts else "N/A"
        extracted_floors = str(raw_prop.get("floors", "N/A"))
        api_floors = str(api_data.get("floors", "N/A")) if verified else "?"
        floors_row = make_row("Floors", extracted_floors, gold_floors, api_floors, check.floors_result, "floors")

        # API verification status
        verify_badge = '<span class="badge badge-pass">Verified</span>' if verified else '<span class="badge badge-warning">Not Verified</span>'
        api_id = raw_prop.get("api_id", "?")
        slug = raw_prop.get("slug", "N/A")

        return f'''
        <div class="property-detail">
            <div class="property-detail-header" onclick="togglePropertyDetail({query_idx}, {prop_idx})">
                <span><strong>{check.property_name[:50]}</strong> {verify_badge}</span>
                <span>CPR: {check.cpr:.0%} {self._result_badge(ConstraintResult.PASS if check.strict_pass else ConstraintResult.FAIL)}</span>
            </div>
            <div class="property-detail-body" id="prop-detail-{query_idx}-{prop_idx}">
                <p style="font-size: 12px; color: var(--gray-500); margin-bottom: 10px;">
                    API ID: {api_id} | Slug: {slug[:50]}...
                </p>
                <div class="detail-grid">
                    <div class="detail-grid-header">Constraint</div>
                    <div class="detail-grid-header">Extracted</div>
                    <div class="detail-grid-header">Gold Standard</div>
                    <div class="detail-grid-header">API Truth</div>
                    <div class="detail-grid-header">Result</div>
                    {type_row}
                    {listing_row}
                    {location_row}
                    {price_row}
                    {bed_row}
                    {floors_row}
                </div>
            </div>
        </div>
        '''

    def _manual_eval_property_card(
        self,
        query_id: int,
        prop_idx: int,
        check: PropertyCheck,
        raw_prop: dict,
        gold_notes: str = "",
    ) -> str:
        """Generate property card for manual evaluation with detailed info and Google Maps."""
        api_data = raw_prop.get("api_data", {})
        verified = raw_prop.get("verified", False)

        # Extract all property information
        prop_name = (
            raw_prop.get("name") or
            raw_prop.get("title") or
            api_data.get("name") or
            api_data.get("title") or
            "Unknown Property"
        )
        prop_type = raw_prop.get("property_type") or api_data.get("property_type") or "N/A"
        listing_type = raw_prop.get("listing_type") or api_data.get("listing_type") or "N/A"
        price = raw_prop.get("price") or api_data.get("price")
        bedrooms = raw_prop.get("bedrooms") or api_data.get("bedrooms")
        bathrooms = raw_prop.get("bathrooms") or api_data.get("bathrooms")
        floors = raw_prop.get("floors") or api_data.get("floors")
        land_size = raw_prop.get("land_size") or raw_prop.get("land_area") or api_data.get("land_size") or api_data.get("land_area")
        building_size = raw_prop.get("building_size") or raw_prop.get("building_area") or api_data.get("building_size") or api_data.get("building_area")
        address = raw_prop.get("address") or api_data.get("address") or api_data.get("display_address") or "N/A"
        location = raw_prop.get("location") or api_data.get("location") or "N/A"
        description = raw_prop.get("description") or api_data.get("description") or "No description available"

        # URL
        url_view = raw_prop.get("url_view") or api_data.get("url_view") or ""
        slug = raw_prop.get("slug") or api_data.get("slug") or ""

        # Coordinates for Google Maps
        lat = raw_prop.get("latitude") or api_data.get("latitude")
        lng = raw_prop.get("longitude") or api_data.get("longitude")

        # Format price
        price_str = self._format_price(price) if price else "N/A"

        # Build specs badges
        specs = []
        if prop_type and prop_type != "N/A":
            specs.append(f'<span class="spec-badge">{prop_type}</span>')
        if listing_type and listing_type != "N/A":
            specs.append(f'<span class="spec-badge">{listing_type}</span>')
        if bedrooms:
            specs.append(f'<span class="spec-badge">{bedrooms} BR</span>')
        if bathrooms:
            specs.append(f'<span class="spec-badge">{bathrooms} BA</span>')
        if floors:
            specs.append(f'<span class="spec-badge">{floors} Floors</span>')
        if land_size:
            specs.append(f'<span class="spec-badge">Land: {land_size}m²</span>')
        if building_size:
            specs.append(f'<span class="spec-badge">Building: {building_size}m²</span>')

        specs_html = "\n".join(specs) if specs else '<span class="spec-badge">No specs</span>'

        # Google Maps embed
        map_html = ""
        if lat and lng:
            map_html = f'''
            <div class="google-map-container">
                <iframe
                    src="https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed"
                    allowfullscreen
                    loading="lazy"
                    referrerpolicy="no-referrer-when-downgrade">
                </iframe>
            </div>
            '''
        else:
            map_html = '<p style="color: var(--gray-500); font-size: 12px;">No coordinates available for map</p>'

        # URL link
        url_html = ""
        if url_view:
            url_html = f'<a href="{url_view}" target="_blank" class="property-url">{url_view}</a>'
        elif slug:
            url_html = f'<p style="font-size: 12px; color: var(--gray-500);">Slug: {slug}</p>'

        # Current manual result status
        manual_status = "PENDING"
        manual_status_class = "manual-pending"
        if check.manual_result == "pass":
            manual_status = "PASS"
            manual_status_class = "manual-pass"
        elif check.manual_result == "fail":
            manual_status = "FAIL"
            manual_status_class = "manual-fail"

        # Description (truncated)
        desc_html = description[:500] + "..." if len(description) > 500 else description

        return f'''
        <div class="manual-eval-card">
            <div class="manual-eval-header">
                <div>
                    <strong>{prop_name[:60]}</strong>
                    <span style="margin-left: 12px; font-size: 13px; color: var(--gray-500);">
                        {price_str}
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span id="manual-status-{query_id}-{prop_idx}" class="{manual_status_class}">{manual_status}</span>
                    <span id="manual-cpr-{query_id}-{prop_idx}" class="cpr-value">Pending</span>
                </div>
            </div>
            <div class="manual-eval-body">
                <div class="property-info-grid">
                    <div class="property-info-section">
                        <h4>Specifications</h4>
                        <div class="property-specs">
                            {specs_html}
                        </div>
                        {url_html}
                    </div>
                    <div class="property-info-section">
                        <h4>Location</h4>
                        <p style="font-size: 13px; margin-bottom: 4px;"><strong>{location}</strong></p>
                        <p style="font-size: 12px; color: var(--gray-600);">{address}</p>
                        {map_html}
                    </div>
                </div>

                <div class="property-info-section" style="margin-bottom: 16px;">
                    <h4>Description</h4>
                    <div class="property-description">{desc_html}</div>
                </div>

                <div class="manual-eval-controls">
                    <p style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;">
                        <strong>Evaluation Criteria:</strong> {gold_notes or 'Manual evaluation required'}
                    </p>
                    <div class="manual-eval-buttons">
                        <button
                            id="manual-pass-{query_id}-{prop_idx}"
                            class="eval-btn eval-btn-pass"
                            onclick="setManualResult({query_id}, {prop_idx}, 'pass')">
                            PASS
                        </button>
                        <button
                            id="manual-fail-{query_id}-{prop_idx}"
                            class="eval-btn eval-btn-fail"
                            onclick="setManualResult({query_id}, {prop_idx}, 'fail')">
                            FAIL
                        </button>
                    </div>
                    <textarea
                        class="eval-comment"
                        placeholder="Add comments about this property evaluation..."
                        onchange="setManualComment({query_id}, {prop_idx}, this.value)"></textarea>
                </div>
            </div>
        </div>
        '''

    def _manual_eval_property_cards(
        self,
        query_id: int,
        checks: list[PropertyCheck],
        raw_properties: list[dict],
        gold_notes: str = "",
    ) -> str:
        """Generate all property cards for manual evaluation."""
        if not checks:
            return '<p style="color: var(--gray-500);">No properties returned</p>'

        cards = []
        for prop_idx, check in enumerate(checks):
            raw_prop = raw_properties[prop_idx] if prop_idx < len(raw_properties) else {}
            cards.append(self._manual_eval_property_card(
                query_id, prop_idx, check, raw_prop, gold_notes
            ))

        return "\n".join(cards)

    def _property_table_detailed(
        self,
        query_idx: int,
        checks: list[PropertyCheck],
        raw_properties: list[dict],
        gold_constraints: dict,
        query_id: int = None,
    ) -> str:
        """Generate detailed property cards with constraint breakdown."""
        if not checks:
            return '<p style="color: var(--gray-500);">No properties returned</p>'

        cards = []
        for prop_idx, check in enumerate(checks):
            # Find matching raw property by name or index
            raw_prop = raw_properties[prop_idx] if prop_idx < len(raw_properties) else {}
            cards.append(self._property_detail_card(
                query_idx, prop_idx, check, raw_prop, gold_constraints, query_id
            ))

        return "\n".join(cards)

    def _property_table(self, checks: list[PropertyCheck]) -> str:
        """Generate simple property constraint table HTML (fallback)."""
        if not checks:
            return '<p style="color: var(--gray-500);">No properties returned</p>'

        rows = []
        for check in checks:
            rows.append(f'''
            <tr>
                <td title="ID: {check.property_id}">{check.property_name[:40]}...</td>
                <td>{self._result_badge(check.property_type_result)}</td>
                <td>{self._result_badge(check.listing_type_result)}</td>
                <td>
                    {self._result_badge(check.location_result)}
                    {f'<br><small>{check.location_keyword_match}</small>' if check.location_keyword_match else ''}
                    {f'<br><small>{check.location_distance_km:.1f}km</small>' if check.location_distance_km else ''}
                </td>
                <td>
                    {self._result_badge(check.price_result)}
                    {f'<br><small>{check.actual_price:,}</small>' if check.actual_price else ''}
                </td>
                <td>
                    {self._result_badge(check.bedrooms_result)}
                    {f'<br><small>{check.actual_bedrooms} BR</small>' if check.actual_bedrooms else ''}
                </td>
                <td>{self._cpr_bar(check.cpr)}</td>
            </tr>
            ''')

        return f'''
        <table>
            <thead>
                <tr>
                    <th>Property</th>
                    <th>Type</th>
                    <th>Listing</th>
                    <th>Location</th>
                    <th>Price</th>
                    <th>Bedrooms</th>
                    <th>CPR</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        '''

    def _query_card(
        self,
        eval_result: QueryEvaluation,
        idx: int,
        threshold: float,
        raw_properties: list[dict] = None,
        gold_constraints: dict = None,
        gold_notes: str = "",
    ) -> str:
        """Generate query evaluation card HTML."""
        is_success = eval_result.is_success(threshold)
        cm_category = eval_result.get_confusion_category(threshold)

        # For manual evaluation questions, use special card layout
        if eval_result.is_manual_evaluation:
            property_content = self._manual_eval_property_cards(
                eval_result.query_id,
                eval_result.property_checks,
                raw_properties or [],
                gold_notes,
            )
        elif raw_properties and gold_constraints:
            # Use detailed view if raw data available
            property_content = self._property_table_detailed(
                idx, eval_result.property_checks, raw_properties, gold_constraints, eval_result.query_id
            )
        else:
            property_content = self._property_table(eval_result.property_checks)

        # Show gold constraints summary
        constraints_summary = ""
        if gold_constraints:
            parts = []
            if gold_constraints.get("property_type"):
                parts.append(f"type={gold_constraints['property_type']}")
            if gold_constraints.get("listing_type"):
                parts.append(f"listing={gold_constraints['listing_type']}")
            if gold_constraints.get("location"):
                loc = gold_constraints["location"]
                keywords = loc.get("keywords", [])
                if keywords:
                    parts.append(f"loc=[{', '.join(keywords[:2])}]")
            if gold_constraints.get("price"):
                price = gold_constraints["price"]
                if price.get("max"):
                    parts.append(f"price<={price['max']/1e9:.1f}B")
                if price.get("min"):
                    parts.append(f"price>={price['min']/1e9:.1f}B")
            if gold_constraints.get("bedrooms"):
                bed = gold_constraints["bedrooms"]
                if bed.get("min"):
                    parts.append(f"bed>={bed['min']}")
            constraints_summary = f'<p style="font-size: 12px; color: var(--gray-600); margin-bottom: 8px;"><strong>Gold Constraints:</strong> {" | ".join(parts)}</p>'

        # Build review controls HTML
        override_status = "auto"
        if eval_result.override_success is not None:
            override_status = "pass" if eval_result.override_success else "fail"

        review_html = f'''
        <div class="review-controls">
            <label>Manual Review:</label>
            <select id="override-{eval_result.query_id}" onchange="setOverride({eval_result.query_id}, this.value)">
                <option value="auto" {'selected' if override_status == 'auto' else ''}>Auto (use CPR)</option>
                <option value="pass" {'selected' if override_status == 'pass' else ''}>Override: PASS</option>
                <option value="fail" {'selected' if override_status == 'fail' else ''}>Override: FAIL</option>
            </select>
            <input type="text" id="notes-{eval_result.query_id}" placeholder="Notes (optional)"
                   value="{eval_result.override_notes or ''}"
                   onchange="setNotes({eval_result.query_id}, this.value)">
        </div>
        '''

        return f'''
        <div class="query-card" data-success="{str(is_success).lower()}" data-category="{eval_result.category}" data-query-id="{eval_result.query_id}">
            <div class="query-header" onclick="toggleQuery({idx})">
                <span class="query-id">#{eval_result.query_id}</span>
                <span class="query-text">{eval_result.question}</span>
                <div class="query-meta">
                    <span class="badge badge-category">{eval_result.category}</span>
                    <span class="badge {'badge-success' if eval_result.expected_result == 'has_data' else 'badge-warning'}">
                        {eval_result.expected_result}
                    </span>
                    <span class="badge {'badge-pass' if is_success else 'badge-fail'}">
                        {cm_category}
                    </span>
                    {self._cpr_bar(eval_result.mean_cpr)}
                </div>
            </div>
            <div class="query-body" id="query-body-{idx}">
                {constraints_summary}
                <p style="margin-bottom: 12px;">
                    <strong>Properties:</strong> {eval_result.num_properties} |
                    <strong>Mean CPR:</strong> {eval_result.mean_cpr:.2%} |
                    <strong>Strict Pass:</strong> {eval_result.strict_success_count}/{eval_result.num_properties}
                </p>
                {property_content}
                {review_html}
            </div>
        </div>
        '''

    def _pca_chart(self, pca: dict) -> str:
        """Generate PCA bar chart HTML."""
        rows = []
        for constraint, value in pca.items():
            if value is not None:
                pct = int(value * 100)
                rows.append(f'''
                <div class="pca-row">
                    <span class="pca-label">{constraint.replace('_', ' ').title()}</span>
                    <div class="pca-bar">
                        <div class="pca-fill" style="width: {pct}%">{pct}%</div>
                    </div>
                </div>
                ''')
            else:
                rows.append(f'''
                <div class="pca-row">
                    <span class="pca-label">{constraint.replace('_', ' ').title()}</span>
                    <div class="pca-bar">
                        <span style="padding: 4px; color: var(--gray-500); font-size: 12px;">N/A</span>
                    </div>
                </div>
                ''')
        return f'<div class="pca-chart">{"".join(rows)}</div>'

    def _confusion_matrix_display(self, cm: dict) -> str:
        """Generate confusion matrix display HTML."""
        return f'''
        <div style="display: flex; gap: 24px; align-items: start;">
            <div>
                <p style="margin-bottom: 8px; font-size: 13px; color: var(--gray-500);">
                    Predicted &rarr;
                </p>
                <div class="cm-grid">
                    <div class="cm-cell cm-tp">TP: {cm['tp']}</div>
                    <div class="cm-cell cm-fp">FP: {cm['fp']}</div>
                    <div class="cm-cell cm-fn">FN: {cm['fn']}</div>
                    <div class="cm-cell cm-tn">TN: {cm['tn']}</div>
                </div>
                <p style="font-size: 13px; color: var(--gray-500);">&uarr; Actual</p>
            </div>
            <div style="flex: 1;">
                <table style="width: auto;">
                    <tr><td>Precision</td><td><strong>{cm['precision']:.2%}</strong></td></tr>
                    <tr><td>Recall</td><td><strong>{cm['recall']:.2%}</strong></td></tr>
                    <tr><td>F1 Score</td><td><strong>{cm['f1_score']:.2%}</strong></td></tr>
                    <tr><td>Accuracy</td><td><strong>{cm['accuracy']:.2%}</strong></td></tr>
                </table>
            </div>
        </div>
        '''

    def generate_report(
        self,
        evaluations: list[QueryEvaluation],
        metrics: EvaluationMetrics,
        output_path: Optional[str | Path] = None,
        title: str = "Evaluation Results",
        timestamp: Optional[str] = None,
        raw_results: list[dict] = None,
        gold_questions: list[dict] = None,
    ) -> str:
        """
        Generate HTML evaluation report.

        Args:
            evaluations: List of query evaluations
            metrics: Calculated metrics
            output_path: Optional path to save HTML file
            title: Report title
            timestamp: Optional timestamp string
            raw_results: Raw test results with extracted properties
            gold_questions: Gold standard questions with constraints

        Returns:
            HTML content as string
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        metrics_dict = metrics.to_dict()

        # Build lookup maps for raw data and gold constraints
        raw_by_query = {}
        gold_by_query = {}
        gold_notes_by_query = {}
        if raw_results:
            for r in raw_results:
                raw_by_query[r.get("query_id", r.get("id"))] = r.get("properties", [])
        if gold_questions:
            for q in gold_questions:
                gold_by_query[q.get("id")] = q.get("constraints", {})
                gold_notes_by_query[q.get("id")] = q.get("notes", "")

        # Build originalData for JavaScript recalculation
        original_data = {}
        for e in evaluations:
            query_data = {
                "query_id": e.query_id,
                "expected_result": e.expected_result,
                "is_manual_evaluation": e.is_manual_evaluation,
                "properties": []
            }
            for check in e.property_checks:
                prop_data = {
                    "property_id": check.property_id,
                    "property_name": check.property_name,
                    "property_type_result": check.property_type_result.value if hasattr(check.property_type_result, 'value') else str(check.property_type_result).lower(),
                    "listing_type_result": check.listing_type_result.value if hasattr(check.listing_type_result, 'value') else str(check.listing_type_result).lower(),
                    "location_result": check.location_result.value if hasattr(check.location_result, 'value') else str(check.location_result).lower(),
                    "price_result": check.price_result.value if hasattr(check.price_result, 'value') else str(check.price_result).lower(),
                    "bedrooms_result": check.bedrooms_result.value if hasattr(check.bedrooms_result, 'value') else str(check.bedrooms_result).lower(),
                    "floors_result": check.floors_result.value if hasattr(check.floors_result, 'value') else str(check.floors_result).lower(),
                    "cpr": check.cpr,
                }
                query_data["properties"].append(prop_data)
            original_data[e.query_id] = query_data

        # Generate query cards with detailed view if data available
        query_cards_list = []
        for i, e in enumerate(evaluations):
            raw_props = raw_by_query.get(e.query_id, None)
            gold_cons = gold_by_query.get(e.query_id, None)
            gold_notes = gold_notes_by_query.get(e.query_id, "")
            query_cards_list.append(
                self._query_card(e, i, metrics.threshold_t, raw_props, gold_cons, gold_notes)
            )
        query_cards = "\n".join(query_cards_list)

        # Category breakdown table
        category_rows = []
        for cat, cat_metrics in metrics.category_metrics.items():
            category_rows.append(f'''
            <tr>
                <td>{cat}</td>
                <td>{cat_metrics['total_queries']}</td>
                <td>{cat_metrics['successful_queries']}</td>
                <td>{cat_metrics['success_rate']:.2%}</td>
                <td>{cat_metrics['mean_cpr']:.2%}</td>
            </tr>
            ''')

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{self.css}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p class="meta">Generated: {timestamp} | Threshold T: {metrics.threshold_t}</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{metrics.total_queries}</div>
                <div class="stat-label">Total Queries</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.total_properties}</div>
                <div class="stat-label">Total Properties</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.mean_cpr:.1%}</div>
                <div class="stat-label">Mean CPR</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.query_success_rate:.1%}</div>
                <div class="stat-label">Query Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.confusion_matrix.f1_score:.1%}</div>
                <div class="stat-label">F1 Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.confusion_matrix.precision:.1%}</div>
                <div class="stat-label">Precision</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.confusion_matrix.recall:.1%}</div>
                <div class="stat-label">Recall</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.strict_success_ratio:.1%}</div>
                <div class="stat-label">Strict Success</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
            <div class="card">
                <div class="card-header">
                    <h2>Confusion Matrix</h2>
                </div>
                <div class="card-body">
                    {self._confusion_matrix_display(metrics_dict['confusion_matrix'])}
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2>Per-Constraint Accuracy (PCA)</h2>
                </div>
                <div class="card-body">
                    {self._pca_chart(metrics_dict['pca'])}
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2>Category Breakdown</h2>
            </div>
            <div class="card-body">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Total</th>
                            <th>Success</th>
                            <th>Rate</th>
                            <th>Mean CPR</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(category_rows)}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2>Query Details</h2>
                <div>
                    <button class="save-btn" onclick="saveAllEvaluations()" style="background: #7c3aed; font-size: 15px; padding: 10px 20px;">Save All Evaluations</button>
                </div>
            </div>
            <div class="card-body">
                <div id="review-summary" class="review-summary" style="display: none;"></div>
                <div class="filter-controls">
                    <button class="filter-btn active" onclick="filterQueries('all')">All</button>
                    <button class="filter-btn" onclick="filterQueries('failed')">Failed Only</button>
                    <button class="filter-btn" onclick="filterQueries('passed')">Passed Only</button>
                </div>
                {query_cards}
            </div>
        </div>
    </div>

    <script>
        window.evaluationData = {json.dumps(metrics_dict)};
        window.originalData = {json.dumps(original_data)};
        {self.js}
    </script>
</body>
</html>
'''

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

        return html
