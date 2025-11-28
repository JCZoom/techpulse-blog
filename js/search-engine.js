/**
 * TechPulse Search Engine
 * Implements Phase 1 & 2 search functionality with advanced syntax
 */

const SearchEngine = {
    allArticles: [],
    searchStartTime: 0,
    
    /**
     * Initialize search engine - load all articles from daily files
     */
    async init() {
        const today = new Date();
        const promises = [];
        
        // Load last 60 days of daily files
        for (let i = 0; i < 60; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            // Try base file and suffixed versions
            for (let suffix of ['', '_2', '_3', '_4', '_5']) {
                const filename = `content/daily/${dateStr}${suffix}.json`;
                promises.push(
                    fetch(filename)
                        .then(res => res.ok ? res.json() : null)
                        .catch(() => null)
                );
            }
        }
        
        const results = await Promise.all(promises);
        const dailyFiles = results.filter(data => data !== null);
        
        // Collect all articles
        dailyFiles.forEach(dailyData => {
            if (dailyData.articles) {
                dailyData.articles.forEach(article => {
                    this.allArticles.push({
                        ...article,
                        date_display: dailyData.date_display,
                        date: dailyData.date
                    });
                });
            }
        });
        
        console.log(`✓ Search index loaded: ${this.allArticles.length} articles from ${dailyFiles.length} files`);
        return this.allArticles.length;
    },
    
    /**
     * Parse search query into structured format
     * Supports: phrases, keywords, tags, sources, dates, scores, OR/NOT operators
     */
    parseQuery(query) {
        const parsed = {
            phrases: [],
            terms: [],
            excludeTerms: [],
            orTerms: [],
            tags: [],
            tagLogic: 'OR',
            sources: [],
            excludeSources: [],
            dateFilter: null,
            dateRange: null,
            scoreFilter: null,
            scoreRange: null,
            rawQuery: query.trim()
        };
        
        if (!query.trim()) return parsed;
        
        let remaining = query;
        
        // Extract exact phrases (quoted text)
        const phraseRegex = /"([^"]+)"/g;
        let match;
        while ((match = phraseRegex.exec(query)) !== null) {
            parsed.phrases.push(match[1].toLowerCase());
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract tag filters
        const tagRegex = /tags?:([^\s]+)/gi;
        while ((match = tagRegex.exec(query)) !== null) {
            const tagValue = match[1];
            if (tagValue.includes('+')) {
                // AND logic
                parsed.tags = tagValue.split('+').map(t => t.trim());
                parsed.tagLogic = 'AND';
            } else if (tagValue.includes(';')) {
                // OR logic
                parsed.tags = tagValue.split(';').map(t => t.trim());
                parsed.tagLogic = 'OR';
            } else {
                parsed.tags.push(tagValue.trim());
            }
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract category filter (exact match)
        const categoryRegex = /category:"([^"]+)"/gi;
        while ((match = categoryRegex.exec(query)) !== null) {
            parsed.tags.push(match[1].trim());
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract source filters
        const sourceRegex = /sources?:([^\s]+)/gi;
        while ((match = sourceRegex.exec(query)) !== null) {
            const sources = match[1].split(';').map(s => s.trim());
            parsed.sources.push(...sources);
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract excluded sources
        const excludeSourceRegex = /-source:([^\s]+)/gi;
        while ((match = excludeSourceRegex.exec(query)) !== null) {
            parsed.excludeSources.push(match[1].trim());
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract date filters
        const dateRegex = /date:([^\s]+)/gi;
        while ((match = dateRegex.exec(query)) !== null) {
            const dateValue = match[1];
            
            // Date range (2025-11-20..2025-11-28)
            if (dateValue.includes('..')) {
                const [from, to] = dateValue.split('..');
                parsed.dateRange = { from, to };
            }
            // Comparison (>2025-11-20, <2025-11-28)
            else if (dateValue.startsWith('>') || dateValue.startsWith('<')) {
                const operator = dateValue[0];
                const date = dateValue.substring(1);
                parsed.dateFilter = { operator, date };
            }
            // Exact date
            else {
                parsed.dateFilter = { operator: '=', date: dateValue };
            }
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract relative date filters (this:week, last:7days)
        const relativeDateRegex = /(this|last):([^\s]+)/gi;
        while ((match = relativeDateRegex.exec(query)) !== null) {
            const [, timeframe, unit] = match;
            parsed.dateFilter = this.parseRelativeDate(timeframe, unit);
            remaining = remaining.replace(match[0], '');
        }
        
        // Extract score filters
        const scoreRegex = /score:([^\s]+)/gi;
        while ((match = scoreRegex.exec(query)) !== null) {
            const scoreValue = match[1];
            
            // Score range (7..9)
            if (scoreValue.includes('..')) {
                const [min, max] = scoreValue.split('..').map(Number);
                parsed.scoreRange = { min, max };
            }
            // Comparison (>7.5, <8)
            else if (scoreValue.startsWith('>') || scoreValue.startsWith('<')) {
                const operator = scoreValue[0];
                const value = parseFloat(scoreValue.substring(1));
                parsed.scoreFilter = { operator, value };
            }
            remaining = remaining.replace(match[0], '');
        }
        
        // Process remaining terms
        remaining = remaining.trim();
        if (remaining) {
            // Split by spaces but handle OR operator
            const words = remaining.split(/\s+/);
            let i = 0;
            while (i < words.length) {
                const word = words[i];
                
                // Handle OR operator
                if (i + 2 < words.length && words[i + 1].toUpperCase() === 'OR') {
                    parsed.orTerms.push([word.toLowerCase(), words[i + 2].toLowerCase()]);
                    i += 3;
                    continue;
                }
                
                // Handle NOT operator (-)
                if (word.startsWith('-')) {
                    parsed.excludeTerms.push(word.substring(1).toLowerCase());
                } else if (word && word !== 'OR') {
                    parsed.terms.push(word.toLowerCase());
                }
                
                i++;
            }
        }
        
        return parsed;
    },
    
    /**
     * Parse relative date expressions (this:week, last:7days)
     */
    parseRelativeDate(timeframe, unit) {
        const now = new Date();
        let date;
        
        if (timeframe === 'this') {
            if (unit === 'week') {
                const startOfWeek = new Date(now);
                startOfWeek.setDate(now.getDate() - now.getDay());
                return { operator: '>', date: startOfWeek.toISOString().split('T')[0] };
            } else if (unit === 'month') {
                const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
                return { operator: '>', date: startOfMonth.toISOString().split('T')[0] };
            }
        } else if (timeframe === 'last') {
            const daysMatch = unit.match(/(\d+)days?/);
            if (daysMatch) {
                const days = parseInt(daysMatch[1]);
                const pastDate = new Date(now);
                pastDate.setDate(now.getDate() - days);
                return { operator: '>', date: pastDate.toISOString().split('T')[0] };
            }
        }
        
        return null;
    },
    
    /**
     * Execute search with parsed query
     */
    search(query, sortBy = 'relevance') {
        this.searchStartTime = performance.now();
        
        const parsed = this.parseQuery(query);
        console.log('Parsed query:', parsed);
        
        // Filter articles
        let results = this.allArticles.filter(article => this.matchArticle(article, parsed));
        
        // Score and sort results
        results = results.map(article => ({
            ...article,
            searchScore: this.scoreResult(article, parsed)
        }));
        
        // Sort based on preference
        if (sortBy === 'relevance') {
            results.sort((a, b) => b.searchScore - a.searchScore);
        } else if (sortBy === 'date') {
            results.sort((a, b) => new Date(b.published) - new Date(a.published));
        } else if (sortBy === 'score') {
            results.sort((a, b) => b.score - a.score);
        }
        
        const searchTime = ((performance.now() - this.searchStartTime) / 1000).toFixed(3);
        
        return {
            results,
            count: results.length,
            searchTime,
            query: parsed
        };
    },
    
    /**
     * Check if article matches all query criteria
     */
    matchArticle(article, parsed) {
        const searchText = `${article.title} ${article.content || ''}`.toLowerCase();
        
        // 1. Check exact phrases
        for (const phrase of parsed.phrases) {
            if (!searchText.includes(phrase)) return false;
        }
        
        // 2. Check required terms (implicit AND)
        for (const term of parsed.terms) {
            if (!searchText.includes(term)) return false;
        }
        
        // 3. Check OR terms
        for (const orPair of parsed.orTerms) {
            const hasAny = orPair.some(term => searchText.includes(term));
            if (!hasAny) return false;
        }
        
        // 4. Check exclusions (NOT)
        for (const term of parsed.excludeTerms) {
            if (searchText.includes(term)) return false;
        }
        
        // 5. Check tags/categories
        if (parsed.tags.length > 0) {
            const articleCategory = article.category.toLowerCase();
            
            if (parsed.tagLogic === 'AND') {
                // All tags must match
                const allMatch = parsed.tags.every(tag => 
                    articleCategory.includes(tag.toLowerCase())
                );
                if (!allMatch) return false;
            } else {
                // Any tag matches (OR)
                const anyMatch = parsed.tags.some(tag => 
                    articleCategory.includes(tag.toLowerCase())
                );
                if (!anyMatch) return false;
            }
        }
        
        // 6. Check sources
        if (parsed.sources.length > 0) {
            const hasSource = parsed.sources.some(source =>
                article.source.toLowerCase().includes(source.toLowerCase())
            );
            if (!hasSource) return false;
        }
        
        // 7. Check excluded sources
        for (const source of parsed.excludeSources) {
            if (article.source.toLowerCase().includes(source.toLowerCase())) {
                return false;
            }
        }
        
        // 8. Check date filters
        if (parsed.dateFilter) {
            const articleDate = article.published.split('T')[0];
            const { operator, date } = parsed.dateFilter;
            
            if (operator === '>') {
                if (articleDate <= date) return false;
            } else if (operator === '<') {
                if (articleDate >= date) return false;
            } else if (operator === '=') {
                if (articleDate !== date) return false;
            }
        }
        
        if (parsed.dateRange) {
            const articleDate = article.published.split('T')[0];
            if (articleDate < parsed.dateRange.from || articleDate > parsed.dateRange.to) {
                return false;
            }
        }
        
        // 9. Check score filters
        if (parsed.scoreFilter) {
            const { operator, value } = parsed.scoreFilter;
            
            if (operator === '>') {
                if (article.score <= value) return false;
            } else if (operator === '<') {
                if (article.score >= value) return false;
            }
        }
        
        if (parsed.scoreRange) {
            if (article.score < parsed.scoreRange.min || article.score > parsed.scoreRange.max) {
                return false;
            }
        }
        
        return true;
    },
    
    /**
     * Score search results for relevance ranking
     */
    scoreResult(article, parsed) {
        let score = 0;
        const titleLower = article.title.toLowerCase();
        const contentLower = (article.content || '').toLowerCase();
        
        // Exact phrase in title = highest score
        for (const phrase of parsed.phrases) {
            if (titleLower.includes(phrase)) score += 20;
            else if (contentLower.includes(phrase)) score += 10;
        }
        
        // Keywords in title
        for (const term of parsed.terms) {
            if (titleLower.includes(term)) score += 10;
            else if (contentLower.includes(term)) score += 3;
        }
        
        // OR terms
        for (const orPair of parsed.orTerms) {
            for (const term of orPair) {
                if (titleLower.includes(term)) score += 10;
                else if (contentLower.includes(term)) score += 3;
            }
        }
        
        // Tag match bonus
        if (parsed.tags.length > 0) {
            score += 5;
        }
        
        // AI relevance score
        score += article.score * 2;
        
        // Recency bonus (newer = higher)
        const daysOld = (Date.now() - new Date(article.published)) / (1000 * 60 * 60 * 24);
        score += Math.max(0, 5 - daysOld * 0.1);
        
        return score;
    },
    
    /**
     * Get all unique categories from loaded articles
     */
    getCategories() {
        const categories = new Set();
        this.allArticles.forEach(article => {
            if (article.category) categories.add(article.category);
        });
        return Array.from(categories).sort();
    },
    
    /**
     * Get all unique sources from loaded articles
     */
    getSources() {
        const sources = new Set();
        this.allArticles.forEach(article => {
            if (article.source) sources.add(article.source);
        });
        return Array.from(sources).sort();
    }
};
