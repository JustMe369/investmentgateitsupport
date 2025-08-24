/**
 * Simple Kibana Integration for IT Support Dashboard
 */
'use strict';

class KibanaIntegration {
    constructor(config = {}) {
        // Default configuration
        this.config = {
            baseUrl: 'http://localhost:5601',
            dashboardId: '7adfa750-4c32-11e8-b3d7-01146121b73d',
            theme: 'v8',
            ...config
        };
        
        // State
        this.isVisible = false;
        this.container = null;
        this.iframe = null;
        
        // Initialize
        this.init();
    }
    
    init() {
        // Remove existing container if any
        const existing = document.getElementById('kibana-container');
        if (existing) existing.remove();
        
        // Create container
        this.container = document.createElement('div');
        this.container.id = 'kibana-container';
        this.container.style.cssText = `
            position: fixed;
            bottom: 0;
            right: 20px;
            width: 90%;
            max-width: 1200px;
            height: 70vh;
            min-height: 400px;
            background: white;
            z-index: 1050;
            box-shadow: -2px -2px 10px rgba(0,0,0,0.1);
            border-radius: 8px 8px 0 0;
            display: none;
            flex-direction: column;
            overflow: hidden;
        `;
        
        // Create header
        const header = document.createElement('div');
        header.style.cssText = `
            padding: 10px 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: move;
            user-select: none;
        `;
        
        // Add title
        const title = document.createElement('div');
        title.innerHTML = '<i class="fas fa-chart-line me-2"></i>Analytics Dashboard';
        
        // Add controls
        const controls = document.createElement('div');
        controls.innerHTML = `
            <button id="kibana-refresh" class="btn btn-sm btn-outline-secondary me-2" title="Refresh">
                <i class="fas fa-sync-alt"></i>
            </button>
            <button id="kibana-close" class="btn btn-sm btn-outline-danger" title="Close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Create iframe container
        const iframeContainer = document.createElement('div');
        iframeContainer.style.flex = '1';
        iframeContainer.style.position = 'relative';
        iframeContainer.style.overflow = 'hidden';
        
        // Create iframe
        this.iframe = document.createElement('iframe');
        this.iframe.id = 'kibana-iframe';
        this.iframe.style.width = '100%';
        this.iframe.style.height = '100%';
        this.iframe.style.border = 'none';
        
        // Assemble everything
        header.appendChild(title);
        header.appendChild(controls);
        iframeContainer.appendChild(this.iframe);
        this.container.appendChild(header);
        this.container.appendChild(iframeContainer);
        document.body.appendChild(this.container);
        
        // Add event listeners
        document.getElementById('kibana-close').addEventListener('click', () => this.hide());
        document.getElementById('kibana-refresh').addEventListener('click', () => this.refresh());
    }
    
    show() {
        if (this.container) {
            this.container.style.display = 'flex';
            this.isVisible = true;
            
            // Load default dashboard if not loaded
            if (!this.iframe.src) {
                this.loadDashboard({
                    dashboardId: this.config.dashboardId,
                    timeRange: { from: 'now-30d', to: 'now' }
                });
            }
        }
    }
    
    hide() {
        if (this.container) {
            this.container.style.display = 'none';
            this.isVisible = false;
        }
    }
    
    toggleDashboard(config = {}) {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
            if (Object.keys(config).length > 0) {
                this.loadDashboard(config);
            }
        }
    }
    
    loadDashboard(config) {
        if (!config || !config.dashboardId) {
            console.error('Dashboard ID is required');
            return;
        }
        
        const timeRange = config.timeRange || { from: 'now-30d', to: 'now' };
        const refreshInterval = { pause: true, value: 0 }; // Default: no auto-refresh
        
        // Build Kibana URL
        let url = `${this.config.baseUrl}/app/dashboards#/view/${config.dashboardId}?`;
        url += `_g=(time:(from:'${timeRange.from}',to:'${timeRange.to}',`;
        url += `refreshInterval:(pause:${refreshInterval.pause},value:${refreshInterval.value})))`;
        
        // Add theme if specified
        if (this.config.theme) {
            url += `&theme:${this.config.theme}`;
        }
        
        // Update iframe source
        if (this.iframe) {
            this.iframe.src = url;
            this.iframe.onload = () => console.log('Kibana dashboard loaded');
            this.iframe.onerror = () => console.error('Failed to load Kibana dashboard');
        }
    }
    
    refresh() {
        if (this.iframe && this.iframe.src) {
            this.iframe.src = this.iframe.src;
        }
    }
}

// Make available globally
if (window) {
    window.KibanaIntegration = KibanaIntegration;
}
        title.style.fontWeight = 'bold';

        const closeButton = document.createElement('button');
        closeButton.textContent = '×';
        closeButton.style.background = 'none';
        closeButton.style.border = 'none';
        closeButton.style.fontSize = '24px';
        closeButton.style.cursor = 'pointer';
        closeButton.style.lineHeight = '1';
        closeButton.addEventListener('click', () => this.toggleDashboard());

        header.appendChild(title);
        header.appendChild(closeButton);

        // Create iframe
        const iframe = document.createElement('iframe');
        iframe.id = this.iframeId;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.style.flexGrow = '1';

        container.appendChild(header);
        container.appendChild(iframe);
        document.body.appendChild(container);
    }

    // Toggle dashboard visibility
    toggleDashboard() {
        const container = document.getElementById(this.iframeContainerId);
        if (container.style.display === 'flex') {
            container.style.display = 'none';
        } else {
            container.style.display = 'flex';
        }
    }

    // Load a specific Kibana dashboard
    loadDashboard(dashboardConfig) {
        const { dashboardId, filters = [] } = dashboardConfig;
        const iframe = document.getElementById(this.iframeId);
        if (!iframe) return;

        // Construct the URL with filters
        let url = `${this.kibanaBaseUrl}/app/dashboards#/view/${dashboardId}?embed=true&_g=()`;
        
        // Add filters if any
        if (filters.length > 0) {
            const filterParams = filters.map(f => 
                `filters:!(${JSON.stringify(f)})`
            ).join(',');
            url += `&${filterParams}`;
        }

        // Set iframe source
        iframe.src = url;
        
        // Save to localStorage
        localStorage.setItem('kibanaDashboard', JSON.stringify(dashboardConfig));
    }

    // Load Kibana visualization
    loadVisualization(visualizationId, indexPattern, timeRange = {}) {
        const iframe = document.getElementById(this.iframeId);
        if (!iframe) return;

        const { from = 'now-15m', to = 'now' } = timeRange;
        const url = `${this.kibanaBaseUrl}/app/visualize#/edit/${visualizationId}?embed=true&_g=(time:(from:'${from}',to:'${to}'))`;
        
        iframe.src = url;
    }
}

// Create global instance
window.kibana = new KibanaIntegration();

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
    window.kibana.init();
});
