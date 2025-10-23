"""
Usage Statistics Tracker

Tracks API usage, token consumption, and cost savings
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class StatsTracker:
    """
    Track usage statistics and cost savings
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize stats tracker
        
        Args:
            config_dir: Directory for storing stats (default: ~/.woosai)
        """
        if config_dir is None:
            config_dir = Path.home() / '.woosai'
        
        self.config_dir = Path(config_dir)
        self.stats_file = self.config_dir / 'stats.json'
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize stats
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load stats from file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default stats structure
        return {
            "total": {
                "requests": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "tokens_saved": 0,
                "cost_without_woosai": 0.0,
                "cost_with_woosai": 0.0,
                "cost_saved": 0.0
            },
            "daily": {},
            "monthly": {},
            "version": "1.0.0"
        }
    
    def _save_stats(self):
        """Save stats to file"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save stats: {e}")
    
    def record_request(self, 
                      tokens_input: int,
                      tokens_output: int,
                      tokens_saved: int,
                      cost_without: float,
                      cost_with: float,
                      strategy: str):
        """
        Record a single API request
        
        Args:
            tokens_input: Input tokens used
            tokens_output: Output tokens used
            tokens_saved: Tokens saved by optimization
            cost_without: Cost without WoosAI
            cost_with: Cost with WoosAI
            strategy: Strategy used (starter/pro/premium)
        """
        now = datetime.now()
        date_key = now.strftime("%Y-%m-%d")
        month_key = now.strftime("%Y-%m")
        
        cost_saved = cost_without - cost_with
        
        # Update total stats
        self.stats["total"]["requests"] += 1
        self.stats["total"]["tokens_input"] += tokens_input
        self.stats["total"]["tokens_output"] += tokens_output
        self.stats["total"]["tokens_saved"] += tokens_saved
        self.stats["total"]["cost_without_woosai"] += cost_without
        self.stats["total"]["cost_with_woosai"] += cost_with
        self.stats["total"]["cost_saved"] += cost_saved
        
        # Update daily stats
        if date_key not in self.stats["daily"]:
            self.stats["daily"][date_key] = {
                "requests": 0,
                "tokens_input": 0,
                "tokens_output": 0,
                "tokens_saved": 0,
                "cost_saved": 0.0,
                "strategies": {}
            }
        
        daily = self.stats["daily"][date_key]
        daily["requests"] += 1
        daily["tokens_input"] += tokens_input
        daily["tokens_output"] += tokens_output
        daily["tokens_saved"] += tokens_saved
        daily["cost_saved"] += cost_saved
        
        # Track strategy usage
        if strategy not in daily["strategies"]:
            daily["strategies"][strategy] = 0
        daily["strategies"][strategy] += 1
        
        # Update monthly stats
        if month_key not in self.stats["monthly"]:
            self.stats["monthly"][month_key] = {
                "requests": 0,
                "cost_saved": 0.0
            }
        
        monthly = self.stats["monthly"][month_key]
        monthly["requests"] += 1
        monthly["cost_saved"] += cost_saved
        
        # Save to file
        self._save_stats()
    
    def get_today_stats(self) -> Dict[str, Any]:
        """Get today's statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily = self.stats["daily"].get(today, {
            "requests": 0,
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0,
            "strategies": {}
        })
        
        return {
            "date": today,
            "requests": daily["requests"],
            "tokens": {
                "input": daily["tokens_input"],
                "output": daily["tokens_output"],
                "saved": daily["tokens_saved"]
            },
            "cost_saved": f"${daily['cost_saved']:.2f}",
            "strategies": daily["strategies"]
        }
    
    def get_monthly_stats(self) -> Dict[str, Any]:
        """Get this month's statistics"""
        month = datetime.now().strftime("%Y-%m")
        monthly = self.stats["monthly"].get(month, {
            "requests": 0,
            "cost_saved": 0.0
        })
        
        # Calculate daily average
        days_in_month = datetime.now().day
        avg_daily = monthly["cost_saved"] / days_in_month if days_in_month > 0 else 0
        
        return {
            "month": month,
            "requests": monthly["requests"],
            "cost_saved": f"${monthly['cost_saved']:.2f}",
            "average_daily": f"${avg_daily:.2f}",
            "projected_monthly": f"${avg_daily * 30:.2f}"
        }
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get total statistics"""
        total = self.stats["total"]
        
        savings_percentage = 0
        if total["cost_without_woosai"] > 0:
            savings_percentage = (total["cost_saved"] / total["cost_without_woosai"]) * 100
        
        return {
            "requests": total["requests"],
            "tokens": {
                "input": total["tokens_input"],
                "output": total["tokens_output"],
                "total": total["tokens_input"] + total["tokens_output"],
                "saved": total["tokens_saved"]
            },
            "cost": {
                "without_woosai": f"${total['cost_without_woosai']:.2f}",
                "with_woosai": f"${total['cost_with_woosai']:.2f}",
                "saved": f"${total['cost_saved']:.2f}",
                "percentage": f"{savings_percentage:.1f}%"
            }
        }
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed statistics with all periods"""
        return {
            "today": self.get_today_stats(),
            "this_month": self.get_monthly_stats(),
            "total": self.get_total_stats(),
            "last_7_days": self._get_last_n_days_stats(7),
            "last_30_days": self._get_last_n_days_stats(30)
        }
    
    def _get_last_n_days_stats(self, n: int) -> Dict[str, Any]:
        """Get stats for last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=n)
        
        total_requests = 0
        total_saved = 0.0
        
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            if date_key in self.stats["daily"]:
                daily = self.stats["daily"][date_key]
                total_requests += daily["requests"]
                total_saved += daily["cost_saved"]
            current_date += timedelta(days=1)
        
        avg_daily = total_saved / n if n > 0 else 0
        
        return {
            "period": f"Last {n} days",
            "requests": total_requests,
            "cost_saved": f"${total_saved:.2f}",
            "average_daily": f"${avg_daily:.2f}"
        }
    
    def display_stats(self):
        """Display formatted statistics"""
        print("\n" + "="*60)
        print("📊 WoosAI Usage Statistics")
        print("="*60)
        
        # Today
        today = self.get_today_stats()
        print(f"\n📅 Today ({today['date']}):")
        print(f"  Requests: {today['requests']}")
        print(f"  Cost Saved: {today['cost_saved']}")
        print(f"  Tokens Saved: {today['tokens']['saved']:,}")
        
        # This Month
        monthly = self.get_monthly_stats()
        print(f"\n📆 This Month ({monthly['month']}):")
        print(f"  Requests: {monthly['requests']}")
        print(f"  Cost Saved: {monthly['cost_saved']}")
        print(f"  Projected Monthly: {monthly['projected_monthly']}")
        
        # Total
        total = self.get_total_stats()
        print(f"\n🎯 Total (All Time):")
        print(f"  Requests: {total['requests']:,}")
        print(f"  Cost Saved: {total['cost']['saved']}")
        print(f"  Savings: {total['cost']['percentage']}")
        
        print("\n" + "="*60 + "\n")