#!/usr/bin/env python3
"""
Learn from User Ratings and Auto-Tune Taste Profile

This script:
1. Reads ratings from localStorage export (JSON)
2. Analyzes which categories/topics you like/dislike
3. Automatically adjusts taste_profile.yaml weights
4. Creates a backup before making changes
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import shutil

def load_ratings(ratings_file):
    """Load ratings from JSON file"""
    try:
        with open(ratings_file, 'r') as f:
            data = json.load(f)
            
        # Handle both direct array and wrapped format
        if isinstance(data, dict) and 'ratings' in data:
            return data['ratings']
        return data
        
    except FileNotFoundError:
        print(f"❌ Ratings file not found: {ratings_file}")
        print("\nHow to export ratings:")
        print("1. Open browser console (F12)")
        print("2. Type: JSON.stringify({ratings: JSON.parse(localStorage.getItem('techpulse_ratings'))})")
        print("3. Copy the output")
        print("4. Save to ratings.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in ratings file: {e}")
        sys.exit(1)


def analyze_ratings(ratings):
    """Analyze ratings to determine category preferences"""
    
    if not ratings:
        print("⚠️  No ratings found!")
        return None, None
    
    # Group by category
    category_ratings = defaultdict(lambda: {'up': 0, 'down': 0, 'scores': [], 'reasons': defaultdict(int)})
    
    for rating in ratings:
        category = rating.get('category', 'Unknown')
        vote = rating.get('rating', 'up')
        score = rating.get('score', 7.0)
        reasons = rating.get('reasons', [])
        
        category_ratings[category][vote] += 1
        category_ratings[category]['scores'].append(score)
        
        # Track reasons
        for reason in reasons:
            category_ratings[category]['reasons'][reason] += 1
    
    # Calculate sentiment for each category
    category_sentiments = {}
    
    for category, data in category_ratings.items():
        total = data['up'] + data['down']
        if total == 0:
            continue
            
        # Calculate sentiment score (-1 to +1)
        sentiment = (data['up'] - data['down']) / total
        
        # Average AI score
        avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 7.0
        
        category_sentiments[category] = {
            'sentiment': sentiment,
            'up_votes': data['up'],
            'down_votes': data['down'],
            'total_votes': total,
            'avg_score': avg_score,
            'top_reasons': dict(sorted(data['reasons'].items(), key=lambda x: x[1], reverse=True)[:3])
        }
    
    # Analyze overall reasons
    reason_analysis = analyze_reasons(ratings)
    
    return category_sentiments, reason_analysis


def analyze_reasons(ratings):
    """Analyze what reasons users give for their ratings"""
    
    reasons_by_vote = {
        'up': defaultdict(int),
        'down': defaultdict(int)
    }
    
    for rating in ratings:
        vote = rating.get('rating', 'up')
        reasons = rating.get('reasons', [])
        
        for reason in reasons:
            reasons_by_vote[vote][reason] += 1
    
    return reasons_by_vote


def calculate_weight_adjustments(sentiments, learning_rate=0.2):
    """
    Calculate how much to adjust each category weight
    
    Args:
        sentiments: Category sentiment analysis
        learning_rate: How aggressively to adjust (0.1 = gentle, 0.5 = aggressive)
    
    Returns:
        Dict of category -> adjustment factor
    """
    adjustments = {}
    
    for category, data in sentiments.items():
        sentiment = data['sentiment']
        votes = data['total_votes']
        
        # Weight adjustment based on sentiment and confidence (more votes = more confident)
        confidence = min(votes / 10.0, 1.0)  # Cap at 10 votes for full confidence
        
        # Calculate adjustment (-0.3 to +0.3 with default learning rate of 0.2)
        adjustment = sentiment * learning_rate * 1.5 * confidence
        
        adjustments[category] = {
            'adjustment': adjustment,
            'new_weight': None,  # Will be calculated when applying
            'sentiment': sentiment,
            'votes': votes
        }
    
    return adjustments


def backup_taste_profile(profile_path):
    """Create timestamped backup of taste profile"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = profile_path.parent / f"taste_profile_backup_{timestamp}.yaml"
    shutil.copy(profile_path, backup_path)
    return backup_path


def apply_adjustments(profile_path, adjustments, dry_run=False):
    """Apply weight adjustments to taste profile"""
    
    # Load current profile
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)
    
    # Track changes
    changes = []
    
    # Adjust priority topics
    if 'priority_topics' in profile:
        for topic in profile['priority_topics']:
            topic_name = topic['name']
            
            # Find matching category (case-insensitive, partial match)
            matched_adjustment = None
            for category, adj_data in adjustments.items():
                if category.lower() in topic_name.lower() or topic_name.lower() in category.lower():
                    matched_adjustment = adj_data
                    break
            
            if matched_adjustment:
                old_weight = topic.get('weight', 1.0)
                new_weight = max(0.5, min(1.5, old_weight + matched_adjustment['adjustment']))
                
                matched_adjustment['new_weight'] = new_weight
                
                if not dry_run:
                    topic['weight'] = round(new_weight, 2)
                
                changes.append({
                    'topic': topic_name,
                    'old_weight': old_weight,
                    'new_weight': new_weight,
                    'adjustment': matched_adjustment['adjustment'],
                    'sentiment': matched_adjustment['sentiment'],
                    'votes': matched_adjustment['votes']
                })
    
    # Adjust secondary topics
    if 'secondary_topics' in profile:
        for topic in profile['secondary_topics']:
            topic_name = topic['name']
            
            matched_adjustment = None
            for category, adj_data in adjustments.items():
                if category.lower() in topic_name.lower() or topic_name.lower() in category.lower():
                    matched_adjustment = adj_data
                    break
            
            if matched_adjustment and matched_adjustment.get('new_weight') is None:
                old_weight = topic.get('weight', 1.0)
                new_weight = max(0.5, min(1.5, old_weight + matched_adjustment['adjustment']))
                
                matched_adjustment['new_weight'] = new_weight
                
                if not dry_run:
                    topic['weight'] = round(new_weight, 2)
                
                changes.append({
                    'topic': topic_name,
                    'old_weight': old_weight,
                    'new_weight': new_weight,
                    'adjustment': matched_adjustment['adjustment'],
                    'sentiment': matched_adjustment['sentiment'],
                    'votes': matched_adjustment['votes']
                })
    
    # Save updated profile
    if not dry_run and changes:
        with open(profile_path, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
    
    return changes, profile


def print_analysis(sentiments, adjustments, changes, reason_analysis=None):
    """Print detailed analysis report"""
    
    print("\n" + "="*60)
    print("📊 RATING ANALYSIS REPORT")
    print("="*60)
    
    # Summary stats
    total_ratings = sum(s['total_votes'] for s in sentiments.values())
    total_up = sum(s['up_votes'] for s in sentiments.values())
    total_down = sum(s['down_votes'] for s in sentiments.values())
    
    print(f"\n📈 Overall Stats:")
    print(f"  Total ratings: {total_ratings}")
    print(f"  👍 Up votes: {total_up}")
    print(f"  👎 Down votes: {total_down}")
    print(f"  Overall sentiment: {(total_up - total_down) / total_ratings:.1%}")
    
    # Overall reasons
    if reason_analysis:
        print(f"\n🔍 Why You Liked Content:")
        for reason, count in sorted(reason_analysis['up'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {reason.replace('_', ' ').title()}: {count} times")
        
        print(f"\n🔍 Why You Disliked Content:")
        for reason, count in sorted(reason_analysis['down'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {reason.replace('_', ' ').title()}: {count} times")
    
    # Category breakdown
    print(f"\n📊 Category Sentiment:")
    for category, data in sorted(sentiments.items(), key=lambda x: x[1]['sentiment'], reverse=True):
        sentiment = data['sentiment']
        emoji = '💚' if sentiment > 0.3 else '💛' if sentiment > -0.3 else '❤️'
        print(f"  {emoji} {category}")
        print(f"     Sentiment: {sentiment:+.2f} ({data['up_votes']}↑ {data['down_votes']}↓)")
        print(f"     Avg AI Score: {data['avg_score']:.1f}")
        
        # Show top reasons for this category
        if data.get('top_reasons'):
            top_reason = list(data['top_reasons'].items())[0] if data['top_reasons'] else None
            if top_reason:
                print(f"     Top reason: {top_reason[0].replace('_', ' ').title()} ({top_reason[1]}x)")
    
    # Proposed changes
    if changes:
        print(f"\n🎯 Proposed Weight Changes:")
        for change in sorted(changes, key=lambda x: abs(x['adjustment']), reverse=True):
            direction = '📈' if change['adjustment'] > 0 else '📉'
            print(f"  {direction} {change['topic']}")
            print(f"     Weight: {change['old_weight']:.2f} → {change['new_weight']:.2f} (Δ {change['adjustment']:+.2f})")
            print(f"     Based on: {change['votes']} votes, {change['sentiment']:+.1%} sentiment")
    else:
        print("\n⚠️  No matching topics found to adjust")
        print("   (Categories in ratings don't match topics in taste profile)")
    
    print("\n" + "="*60)


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Learn from article ratings and auto-tune taste profile')
    parser.add_argument('ratings_file', help='Path to ratings JSON file (exported from localStorage)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without actually changing')
    parser.add_argument('--learning-rate', type=float, default=0.2, help='Learning rate (0.1-0.5, default: 0.2)')
    
    args = parser.parse_args()
    
    # Paths
    script_dir = Path(__file__).parent
    profile_path = script_dir / 'scoring' / 'taste_profile.yaml'
    
    print("🧠 TechPulse Learning System")
    print("="*60)
    
    # Load ratings
    print(f"\n📖 Loading ratings from: {args.ratings_file}")
    ratings = load_ratings(args.ratings_file)
    print(f"✓ Loaded {len(ratings)} ratings")
    
    # Analyze
    print("\n🔍 Analyzing preferences...")
    sentiments, reason_analysis = analyze_ratings(ratings)
    
    if not sentiments:
        print("❌ No valid ratings to analyze")
        return
    
    # Calculate adjustments
    print(f"\n⚙️  Calculating weight adjustments (learning rate: {args.learning_rate})...")
    adjustments = calculate_weight_adjustments(sentiments, args.learning_rate)
    
    # Apply (or dry-run)
    if not args.dry_run:
        backup_path = backup_taste_profile(profile_path)
        print(f"\n💾 Created backup: {backup_path.name}")
    
    print(f"\n{'🔍 DRY RUN - ' if args.dry_run else '✍️  Applying changes to: '}{profile_path.name}")
    changes, updated_profile = apply_adjustments(profile_path, adjustments, dry_run=args.dry_run)
    
    # Print analysis
    print_analysis(sentiments, adjustments, changes, reason_analysis)
    
    # Summary
    if changes:
        if args.dry_run:
            print("\n⚠️  DRY RUN - No changes were made")
            print("   Remove --dry-run to apply these changes")
        else:
            print(f"\n✅ Applied {len(changes)} weight adjustments!")
            print(f"   Backup saved: {backup_path.name}")
            print("\n📋 Next steps:")
            print("   1. Review the changes in taste_profile.yaml")
            print("   2. Run the pipeline to see improved results")
            print("   3. Continue rating articles to keep improving!")
    else:
        print("\n💡 Tip: Make sure your ratings use categories that match topics in taste_profile.yaml")
    
    print()


if __name__ == '__main__':
    main()
