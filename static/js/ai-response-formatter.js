/**
 * Enhanced AI Response Formatter
 * Improves readability and visual presentation of AI research results
 */

class AIResponseFormatter {
    
    /**
     * Format the main agent analysis response
     */
    static formatAgentAnalysis(content) {
        // Clean up the content first
        let formatted = content
            // Handle bullet points and lists
            .replace(/\*\s+\*\*(.*?)\*\*:\s*/g, '<div class="insight-header"><i class="fas fa-lightbulb"></i> <strong>$1:</strong></div><div class="insight-content">')
            .replace(/\*\s+(.*?)(?=\*\s+|\n\n|$)/g, '<li>$1</li>')
            
            // Handle section headers
            .replace(/\*\*(.*?)\*\*\n/g, '<h4 class="analysis-section"><i class="fas fa-chart-line"></i> $1</h4>')
            
            // Handle emphasis
            .replace(/\*\*(.*?)\*\*/g, '<strong class="highlight">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            
            // Handle percentages and numbers
            .replace(/(\d+\.?\d*%)/g, '<span class="metric">$1</span>')
            .replace(/(\d+)\s+(ideas?|contributors?)/g, '<span class="count">$1</span> $2')
            
            // Clean up and structure
            .replace(/\n\n/g, '</div><div class="analysis-paragraph">')
            .replace(/\n/g, '<br>');

        // Wrap in structured container
        return `
            <div class="ai-analysis-container">
                <div class="analysis-paragraph">${formatted}</div>
            </div>
        `;
    }

    /**
     * Format research steps into a clean timeline
     */
    static formatResearchSteps(steps) {
        if (!steps || steps.length === 0) return '';
        
        let stepsHtml = `
            <div class="research-timeline">
                <h4 class="timeline-header">
                    <i class="fas fa-cogs"></i> Research Process
                </h4>
        `;
        
        steps.forEach((step, index) => {
            const toolIcon = this.getToolIcon(step.tool);
            const formattedResult = this.formatToolResult(step.result);
            
            stepsHtml += `
                <div class="timeline-step">
                    <div class="step-header">
                        <span class="step-number">${index + 1}</span>
                        <span class="step-tool">
                            <i class="${toolIcon}"></i>
                            ${this.getToolDisplayName(step.tool)}
                        </span>
                    </div>
                    <div class="step-content">
                        ${formattedResult}
                    </div>
                </div>
            `;
        });
        
        stepsHtml += '</div>';
        return stepsHtml;
    }

    /**
     * Format individual tool results
     */
    static formatToolResult(result) {
        // Handle innovation trends format
        if (result.includes('Categories Distribution:')) {
            return this.formatTrendsResult(result);
        }
        
        // Handle similar ideas format
        if (result.includes('similar ideas:')) {
            return this.formatSimilarIdeasResult(result);
        }
        
        // Handle idea details format
        if (result.includes('Title:') && result.includes('Description:')) {
            return this.formatIdeaDetailsResult(result);
        }
        
        // Handle contributor analysis
        if (result.includes('contributors with')) {
            return this.formatContributorResult(result);
        }
        
        // Default formatting for other results
        return this.formatGenericResult(result);
    }

    /**
     * Format trends analysis results
     */
    static formatTrendsResult(result) {
        let formatted = result
            // Handle section headers
            .replace(/^(.*Analysis:)$/gm, '<h5 class="trend-section">$1</h5>')
            
            // Handle metrics
            .replace(/Total Ideas: (\d+)/g, '<div class="metric-item"><span class="metric-label">Total Ideas:</span> <span class="metric-value">$1</span></div>')
            .replace(/Recent Activity: (.*)/g, '<div class="metric-item"><span class="metric-label">Recent Activity:</span> <span class="metric-value">$1</span></div>')
            .replace(/Active Contributors: (.*)/g, '<div class="metric-item"><span class="metric-label">Active Contributors:</span> <span class="metric-value">$1</span></div>')
            
            // Handle category distributions
            .replace(/• (.*?): (\d+) ideas \((.*?)\)/g, '<div class="category-item"><span class="category-name">$1</span><span class="category-count">$2 ideas</span><span class="category-percent">$3</span></div>')
            
            // Handle other bullet points
            .replace(/• (.*?): (.*)/g, '<div class="status-item"><span class="status-label">$1:</span> <span class="status-value">$2</span></div>');
            
        return `<div class="trends-result">${formatted}</div>`;
    }

    /**
     * Format similar ideas results
     */
    static formatSimilarIdeasResult(result) {
        let formatted = result;
        
        // Extract the count
        const countMatch = result.match(/Found (\d+) similar ideas/);
        let html = '';
        
        if (countMatch) {
            html += `<div class="result-summary">Found <span class="count">${countMatch[1]}</span> similar ideas:</div>`;
        }
        
        // Format individual ideas
        const ideaMatches = result.matchAll(/• (.*?) \((.*?) match\) - (.*?) by (.*)/g);
        html += '<div class="ideas-list">';
        
        for (const match of ideaMatches) {
            const [, title, similarity, category, contributor] = match;
            html += `
                <div class="idea-item">
                    <div class="idea-header">
                        <span class="idea-title">${title}</span>
                        <span class="similarity-score">${similarity} match</span>
                    </div>
                    <div class="idea-meta">
                        <span class="idea-category"><i class="fas fa-tag"></i> ${category}</span>
                        <span class="idea-contributor"><i class="fas fa-user"></i> ${contributor}</span>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Format idea details results
     */
    static formatIdeaDetailsResult(result) {
        const lines = result.split('\n').filter(line => line.trim());
        let html = '<div class="idea-details">';
        
        lines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed.includes(':')) {
                const [label, value] = trimmed.split(':').map(s => s.trim());
                const icon = this.getFieldIcon(label);
                html += `
                    <div class="detail-item">
                        <span class="detail-label"><i class="${icon}"></i> ${label}:</span>
                        <span class="detail-value">${value}</span>
                    </div>
                `;
            }
        });
        
        html += '</div>';
        return html;
    }

    /**
     * Format contributor analysis results
     */
    static formatContributorResult(result) {
        let html = '';
        
        // Extract summary
        const summaryMatch = result.match(/Found (\d+) contributors/);
        if (summaryMatch) {
            html += `<div class="result-summary">Found <span class="count">${summaryMatch[1]}</span> contributors:</div>`;
        }
        
        // Format individual contributors
        const contributorMatches = result.matchAll(/• (.*?) - (.*?) \((.*?)\)/g);
        html += '<div class="contributors-list">';
        
        for (const match of contributorMatches) {
            const [, name, skills, availability] = match;
            html += `
                <div class="contributor-item">
                    <div class="contributor-name">
                        <i class="fas fa-user"></i> ${name}
                    </div>
                    <div class="contributor-skills">
                        <i class="fas fa-code"></i> ${skills}
                    </div>
                    <div class="contributor-availability">
                        <i class="fas fa-clock"></i> ${availability}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Format generic results
     */
    static formatGenericResult(result) {
        return result
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    /**
     * Get icon for tool
     */
    static getToolIcon(toolName) {
        const icons = {
            'search_similar_ideas': 'fas fa-search',
            'get_idea_details': 'fas fa-info-circle',
            'analyze_contributor_skills': 'fas fa-users',
            'get_innovation_trends': 'fas fa-chart-line',
            'evaluate_idea_feasibility': 'fas fa-balance-scale',
            'create_implementation_roadmap': 'fas fa-road'
        };
        return icons[toolName] || 'fas fa-cog';
    }

    /**
     * Get display name for tool
     */
    static getToolDisplayName(toolName) {
        const names = {
            'search_similar_ideas': 'Similar Ideas Search',
            'get_idea_details': 'Idea Details Lookup',
            'analyze_contributor_skills': 'Contributor Analysis',
            'get_innovation_trends': 'Trends Analysis',
            'evaluate_idea_feasibility': 'Feasibility Assessment',
            'create_implementation_roadmap': 'Implementation Planning'
        };
        return names[toolName] || toolName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Get icon for detail fields
     */
    static getFieldIcon(fieldName) {
        const icons = {
            'Title': 'fas fa-heading',
            'Description': 'fas fa-align-left',
            'Category': 'fas fa-tag',
            'Impact': 'fas fa-star',
            'Status': 'fas fa-flag',
            'Contributor': 'fas fa-user',
            'Abstract': 'fas fa-file-text'
        };
        return icons[fieldName] || 'fas fa-info';
    }

    /**
     * Format tools used summary
     */
    static formatToolsUsed(tools) {
        if (!tools || tools.length === 0) return '';
        
        let html = `
            <div class="tools-summary">
                <h4 class="tools-header">
                    <i class="fas fa-toolbox"></i> Tools Used
                </h4>
                <div class="tools-list">
        `;
        
        tools.forEach(tool => {
            const icon = this.getToolIcon(tool);
            const displayName = this.getToolDisplayName(tool);
            html += `
                <span class="tool-badge">
                    <i class="${icon}"></i>
                    ${displayName}
                </span>
            `;
        });
        
        html += '</div></div>';
        return html;
    }
}

// Export for use in templates
window.AIResponseFormatter = AIResponseFormatter;
