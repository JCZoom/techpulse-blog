/**
 * TechPulse Search UI
 * Handles keyboard shortcuts, syntax helper, and results rendering
 */

const SearchUI = {
    syntaxHelperVisible: false,
    selectedHelperIndex: -1,
    currentSort: 'relevance',
    
    /**
     * Syntax helper items (ChatGPT-style)
     */
    syntaxItems: [
        {
            icon: '🔤',
            title: 'Exact Phrase',
            desc: 'Search for an exact phrase in quotes',
            syntax: '"AI agents"',
            pattern: '"'
        },
        {
            icon: '🏷️',
            title: 'Single Tag',
            desc: 'Filter by one category/tag',
            syntax: 'tag:enterprise',
            pattern: 'tag:'
        },
        {
            icon: '🏷️',
            title: 'Multiple Tags (OR)',
            desc: 'Match any of these tags',
            syntax: 'tags:ai;ml;crypto',
            pattern: 'tags:'
        },
        {
            icon: '🏷️',
            title: 'Multiple Tags (AND)',
            desc: 'Match all these tags',
            syntax: 'tags:ai+enterprise',
            pattern: 'tags:'
        },
        {
            icon: '📰',
            title: 'Filter by Source',
            desc: 'Show articles from specific source',
            syntax: 'source:VentureBeat',
            pattern: 'source:'
        },
        {
            icon: '📰',
            title: 'Multiple Sources',
            desc: 'Match any of these sources',
            syntax: 'sources:OpenAI;Anthropic',
            pattern: 'sources:'
        },
        {
            icon: '📅',
            title: 'Exact Date',
            desc: 'Articles from specific date',
            syntax: 'date:2025-11-28',
            pattern: 'date:'
        },
        {
            icon: '📅',
            title: 'Date After',
            desc: 'Articles published after date',
            syntax: 'date:>2025-11-20',
            pattern: 'date:>'
        },
        {
            icon: '📅',
            title: 'Date Range',
            desc: 'Articles within date range',
            syntax: 'date:2025-11-20..2025-11-28',
            pattern: 'date:'
        },
        {
            icon: '📅',
            title: 'This Week',
            desc: 'Articles from current week',
            syntax: 'this:week',
            pattern: 'this:'
        },
        {
            icon: '📅',
            title: 'Last N Days',
            desc: 'Recent articles',
            syntax: 'last:7days',
            pattern: 'last:'
        },
        {
            icon: '⭐',
            title: 'Score Greater Than',
            desc: 'High quality articles',
            syntax: 'score:>7.5',
            pattern: 'score:>'
        },
        {
            icon: '⭐',
            title: 'Score Range',
            desc: 'Articles in score range',
            syntax: 'score:7..9',
            pattern: 'score:'
        },
        {
            icon: '➕',
            title: 'OR Operator',
            desc: 'Match either term',
            syntax: 'crypto OR blockchain',
            pattern: ' OR '
        },
        {
            icon: '➖',
            title: 'Exclude Term',
            desc: 'Remove articles containing term',
            syntax: '-hype',
            pattern: '-'
        },
        {
            icon: '🎯',
            title: 'Combined Search',
            desc: 'Use multiple filters together',
            syntax: '"AI agents" tag:enterprise score:>8',
            pattern: ''
        }
    ],
    
    /**
     * Initialize search UI
     */
    init() {
        const searchInput = document.getElementById('mainSearchInput');
        if (!searchInput) return;
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Setup search input handlers
        searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
        searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
        searchInput.addEventListener('blur', () => {
            // Delay hiding to allow click on dropdown
            setTimeout(() => this.hideSyntaxHelper(), 200);
        });
        
        // Setup sort buttons (if on search page)
        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleSort(e));
        });
        
        // If on search page, execute search from URL
        if (window.location.pathname.includes('search.html')) {
            this.executeSearchFromURL();
        }
    },
    
    /**
     * Setup keyboard shortcuts (/ to focus search, ESC to unfocus)
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            const searchInput = document.getElementById('mainSearchInput');
            if (!searchInput) return;
            
            // / key to focus search (unless already in input)
            if (e.key === '/' && document.activeElement !== searchInput && 
                !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
            
            // ESC to close syntax helper or unfocus search bar
            if (e.key === 'Escape') {
                if (this.syntaxHelperVisible) {
                    e.preventDefault();
                    this.hideSyntaxHelper();
                } else if (document.activeElement === searchInput) {
                    e.preventDefault();
                    searchInput.blur(); // Unfocus the search bar
                }
            }
        });
    },
    
    /**
     * Handle search input keydown (Enter, arrows, etc.)
     */
    handleSearchKeydown(e) {
        const input = e.target;
        
        // Enter key - execute search
        if (e.key === 'Enter') {
            e.preventDefault();
            this.executeSearch(input.value);
            return;
        }
        
        // / key when focused - toggle syntax helper
        if (e.key === '/' && document.activeElement === input) {
            // Only prevent default if not selecting text
            if (window.getSelection().toString().length === 0) {
                e.preventDefault();
                this.toggleSyntaxHelper(input);
            }
            return;
        }
        
        // Arrow keys - navigate syntax helper
        if (this.syntaxHelperVisible) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateSyntaxHelper(1);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateSyntaxHelper(-1);
            } else if (e.key === 'Enter' && this.selectedHelperIndex >= 0) {
                e.preventDefault();
                this.selectSyntaxItem(this.selectedHelperIndex);
            }
        }
    },
    
    /**
     * Handle search input changes (filter syntax helper)
     */
    handleSearchInput(e) {
        if (this.syntaxHelperVisible) {
            this.filterSyntaxHelper(e.target.value);
        }
    },
    
    /**
     * Toggle syntax helper dropdown
     */
    toggleSyntaxHelper(input) {
        if (this.syntaxHelperVisible) {
            this.hideSyntaxHelper();
        } else {
            this.showSyntaxHelper(input);
        }
    },
    
    /**
     * Show syntax helper modal
     */
    showSyntaxHelper(input) {
        this.syntaxHelperVisible = true;
        this.selectedHelperIndex = -1;
        this.renderSyntaxHelper(input.value);
    },
    
    /**
     * Hide syntax helper modal
     */
    hideSyntaxHelper() {
        const overlay = document.getElementById('syntaxHelperOverlay');
        if (overlay) {
            overlay.remove();
        }
        this.syntaxHelperVisible = false;
        this.selectedHelperIndex = -1;
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Refocus search input
        const searchInput = document.getElementById('mainSearchInput');
        if (searchInput) searchInput.focus();
    },
    
    /**
     * Render syntax helper as modal window
     */
    renderSyntaxHelper(query = '') {
        // Remove existing overlay if any
        const existingOverlay = document.getElementById('syntaxHelperOverlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        const filtered = this.filterSyntaxItems(query);
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.id = 'syntaxHelperOverlay';
        overlay.className = 'syntax-helper-overlay';
        overlay.onclick = (e) => {
            if (e.target === overlay) this.hideSyntaxHelper();
        };
        
        // Create modal
        let html = `
            <div class="syntax-helper" onclick="event.stopPropagation()">
                <div class="syntax-helper-header">
                    <span>Search Syntax</span>
                    <span class="syntax-helper-close">Press ESC to close</span>
                </div>
                <div class="syntax-helper-list">
        `;
        
        filtered.forEach((item, index) => {
            const activeClass = index === this.selectedHelperIndex ? 'active' : '';
            html += `
                <div class="syntax-helper-item ${activeClass}" data-index="${index}" 
                     onclick="SearchUI.insertSyntax('${this.escapeSyntax(item.syntax)}')">
                    <div class="syntax-helper-icon">${item.icon}</div>
                    <div class="syntax-helper-content">
                        <div class="syntax-helper-title">${item.title}</div>
                        <div class="syntax-helper-desc">${item.desc}</div>
                        <div class="syntax-helper-syntax">${item.syntax}</div>
                    </div>
                </div>
            `;
        });
        
        if (filtered.length === 0) {
            html += '<div class="syntax-helper-item"><div class="syntax-helper-content"><div class="syntax-helper-desc">No matching syntax found</div></div></div>';
        }
        
        html += `
                </div>
            </div>
        `;
        
        overlay.innerHTML = html;
        document.body.appendChild(overlay);
        
        // Prevent body scroll when modal is open
        document.body.style.overflow = 'hidden';
    },
    
    /**
     * Filter syntax items based on current query
     */
    filterSyntaxItems(query) {
        if (!query.trim()) return this.syntaxItems;
        
        const lowerQuery = query.toLowerCase();
        return this.syntaxItems.filter(item => {
            return item.title.toLowerCase().includes(lowerQuery) ||
                   item.desc.toLowerCase().includes(lowerQuery) ||
                   item.syntax.toLowerCase().includes(lowerQuery) ||
                   (item.pattern && query.includes(item.pattern));
        });
    },
    
    /**
     * Escape syntax for HTML attribute
     */
    escapeSyntax(syntax) {
        return syntax.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    },
    
    /**
     * Navigate syntax helper with arrow keys
     */
    navigateSyntaxHelper(direction) {
        const items = document.querySelectorAll('.syntax-helper-item[data-index]');
        if (items.length === 0) return;
        
        // Remove current active class
        if (this.selectedHelperIndex >= 0 && this.selectedHelperIndex < items.length) {
            items[this.selectedHelperIndex].classList.remove('active');
        }
        
        // Update index
        this.selectedHelperIndex += direction;
        
        // Wrap around
        if (this.selectedHelperIndex < 0) this.selectedHelperIndex = items.length - 1;
        if (this.selectedHelperIndex >= items.length) this.selectedHelperIndex = 0;
        
        // Add active class and scroll into view
        if (this.selectedHelperIndex >= 0 && this.selectedHelperIndex < items.length) {
            const activeItem = items[this.selectedHelperIndex];
            activeItem.classList.add('active');
            activeItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    },
    
    /**
     * Select syntax item (insert into search box)
     */
    selectSyntaxItem(index) {
        const filtered = this.filterSyntaxItems(document.getElementById('mainSearchInput').value);
        if (index >= 0 && index < filtered.length) {
            this.insertSyntax(filtered[index].syntax);
        }
    },
    
    /**
     * Insert syntax into search box
     */
    insertSyntax(syntax) {
        const input = document.getElementById('mainSearchInput');
        if (!input) return;
        
        // If input is empty or ends with space, just append
        // Otherwise, add space before
        const currentValue = input.value.trim();
        input.value = currentValue ? `${currentValue} ${syntax}` : syntax;
        input.focus();
        
        // Move cursor to end
        input.setSelectionRange(input.value.length, input.value.length);
        
        this.hideSyntaxHelper();
    },
    
    /**
     * Filter syntax helper based on query
     */
    filterSyntaxHelper(query) {
        if (this.syntaxHelperVisible) {
            this.selectedHelperIndex = -1; // Reset selection when filtering
            this.renderSyntaxHelper(query);
        }
    },
    
    /**
     * Execute search - navigate to search page with query
     */
    executeSearch(query) {
        if (!query.trim()) return;
        
        // Encode query for URL
        const encodedQuery = encodeURIComponent(query);
        
        // Navigate to search page
        window.location.href = `search.html?q=${encodedQuery}`;
    },
    
    /**
     * Execute search from URL parameters (on search page)
     */
    async executeSearchFromURL() {
        // Get query from URL
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');
        const sort = urlParams.get('sort') || 'relevance';
        
        if (!query) {
            window.location.href = 'index.html';
            return;
        }
        
        // Update search input
        const searchInput = document.getElementById('mainSearchInput');
        if (searchInput) searchInput.value = decodeURIComponent(query);
        
        // Display query
        const queryDisplay = document.getElementById('queryDisplay');
        if (queryDisplay) queryDisplay.textContent = decodeURIComponent(query);
        
        // Add 10 second timeout
        const loadingTimeout = setTimeout(() => {
            console.error('Search timed out after 10 seconds');
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('noResults').style.display = 'block';
            document.getElementById('noResults').innerHTML = `
                <h2>Search timed out</h2>
                <p>The search is taking too long. This might be a network issue.</p>
                <p>Try:</p>
                <ul style="text-align: left; max-width: 400px; margin: 1rem auto;">
                    <li>Refresh the page</li>
                    <li>Check your internet connection</li>
                    <li>Check browser console (F12) for errors</li>
                </ul>
                <p><a href="index.html" class="btn-primary" style="display: inline-block; margin-top: 1rem;">Go back to homepage</a></p>
            `;
        }, 10000); // 10 second timeout
        
        // Initialize search engine
        try {
            console.log('Initializing search engine...');
            const articleCount = await SearchEngine.init();
            clearTimeout(loadingTimeout); // Clear timeout on success
            console.log(`Loaded ${articleCount} articles`);
            
            if (articleCount === 0) {
                document.getElementById('loadingState').style.display = 'none';
                document.getElementById('noResults').style.display = 'block';
                document.getElementById('noResults').innerHTML = `
                    <h2>No articles found</h2>
                    <p>No articles are available to search yet.</p>
                    <p><a href="index.html" class="btn-primary" style="display: inline-block; margin-top: 1rem;">Go back to homepage</a></p>
                `;
                return;
            }
            
            // Perform search
            console.log('Executing search...');
            const results = SearchEngine.search(query, sort);
            console.log(`Found ${results.count} results`);
            
            // Render results
            this.renderResults(results);
            
        } catch (error) {
            clearTimeout(loadingTimeout); // Clear timeout on error
            console.error('Search error:', error);
            document.getElementById('loadingState').style.display = 'none';
            document.getElementById('noResults').style.display = 'block';
            document.getElementById('noResults').innerHTML = `
                <h2>Search error</h2>
                <p>Unable to load search index: ${error.message}</p>
                <p>Check browser console (F12) for more details.</p>
                <p><a href="index.html" class="btn-primary" style="display: inline-block; margin-top: 1rem;">Go back to homepage</a></p>
            `;
        }
    },
    
    /**
     * Render search results
     */
    renderResults(searchResults) {
        const { results, count, searchTime } = searchResults;
        
        // Hide loading
        document.getElementById('loadingState').style.display = 'none';
        
        // Show/hide appropriate sections
        if (count === 0) {
            document.getElementById('noResults').style.display = 'block';
            document.getElementById('resultsStats').style.display = 'none';
            document.getElementById('resultsList').style.display = 'none';
            return;
        }
        
        // Show results
        document.getElementById('resultCount').textContent = count;
        document.getElementById('searchTime').textContent = `Found in ${searchTime}s`;
        document.getElementById('resultsStats').style.display = 'flex';
        document.getElementById('resultsList').style.display = 'block';
        
        // Render result items
        const resultsList = document.getElementById('resultsList');
        resultsList.innerHTML = '';
        
        results.forEach(article => {
            resultsList.appendChild(this.createResultCard(article));
        });
    },
    
    /**
     * Create result card (compact format like runners-up)
     */
    createResultCard(article) {
        const link = document.createElement('a');
        link.href = article.url;
        link.target = '_blank';
        link.className = 'compact-article';
        
        const scoreClass = article.score >= 8 ? 'high' : article.score >= 7 ? 'medium' : '';
        const readTime = this.estimateReadTime(article.word_count);
        const timeAgo = ContentLoader.getTimeAgo(article.published);
        const sourceUrl = ContentLoader.getSourceUrl(article.source);
        
        link.innerHTML = `
            <div class="score-badge ${scoreClass}">${article.score}</div>
            <div class="compact-thumbnail">
                ${article.image_url 
                    ? `<img src="${article.image_url}" alt="${article.title}" onerror="this.parentElement.innerHTML='<div class=\\'compact-thumbnail-placeholder\\'>${article.category}</div>';">` 
                    : `<div class="compact-thumbnail-placeholder">${article.category}</div>`
                }
            </div>
            <div class="compact-content">
                <h3 class="compact-title">${article.title}</h3>
                <div class="compact-meta">
                    <span class="compact-category">${article.category}</span>
                    <span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <a href="${sourceUrl}" target="_blank" style="color: inherit; text-decoration: none;" onclick="event.stopPropagation();">${article.source}</a>
                    </span>
                    <span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        ${readTime}
                    </span>
                    <span>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        ${timeAgo}
                    </span>
                </div>
            </div>
        `;
        
        return link;
    },
    
    /**
     * Estimate read time from word count
     */
    estimateReadTime(wordCount) {
        if (!wordCount) return '1 min';
        const minutes = Math.ceil(wordCount / 200);
        return `${minutes} min`;
    },
    
    /**
     * Handle sort button clicks
     */
    handleSort(e) {
        const btn = e.target;
        const sortBy = btn.dataset.sort;
        
        // Update active button
        document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update URL and re-search
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('sort', sortBy);
        window.history.replaceState({}, '', `${window.location.pathname}?${urlParams}`);
        
        // Re-execute search
        this.executeSearchFromURL();
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SearchUI.init());
} else {
    SearchUI.init();
}
