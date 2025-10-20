"""
WoosAI License Generator
Generate license keys for Premium plan

Usage:
    python tools/license_generator.py --plan PREMIUM --days 30
"""

import hashlib
import argparse
from datetime import datetime, timedelta


class LicenseGenerator:
    """Generate WoosAI license keys"""
    
    # Same secret as in woosailibrary.py
    SECRET_KEY = "WOOSAI_SECRET_2025_V1"
    
    @staticmethod
    def generate(plan: str, duration_days: int) -> str:
        """
        Generate license key
        
        Args:
            plan: "FREE" or "PREMIUM"
            duration_days: License duration in days
        
        Returns:
            License key: WOOSAI-PLAN-YYYYMMDD-SIGNATURE
        """
        # Calculate expiry date
        expiry = datetime.now() + timedelta(days=duration_days)
        expiry_str = expiry.strftime("%Y%m%d")
        
        # Generate signature
        data = f"{plan}:{expiry_str}:{LicenseGenerator.SECRET_KEY}"
        signature = hashlib.sha256(data.encode()).hexdigest()[:6].upper()
        
        # Compose license key
        license_key = f"WOOSAI-{plan}-{expiry_str}-{signature}"
        
        return license_key
    
    @staticmethod
    def verify(license_key: str) -> dict:
        """
        Verify license key
        
        Returns:
            dict with verification result
        """
        try:
            parts = license_key.split('-')
            if len(parts) != 4:
                return {"valid": False, "error": "Invalid format"}
            
            prefix, plan, expiry, signature = parts
            
            if prefix != "WOOSAI":
                return {"valid": False, "error": "Invalid prefix"}
            
            # Check signature
            data = f"{plan}:{expiry}:{LicenseGenerator.SECRET_KEY}"
            expected_sig = hashlib.sha256(data.encode()).hexdigest()[:6].upper()
            
            if signature != expected_sig:
                return {"valid": False, "error": "Invalid signature"}
            
            # Check expiry
            expiry_date = datetime.strptime(expiry, "%Y%m%d")
            is_expired = datetime.now() > expiry_date
            
            return {
                "valid": True,
                "plan": plan,
                "expiry": expiry_date.strftime("%Y-%m-%d"),
                "expired": is_expired,
                "days_remaining": (expiry_date - datetime.now()).days
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Generate WoosAI license keys")
    parser.add_argument("--plan", choices=["FREE", "PREMIUM"], default="PREMIUM",
                       help="License plan (default: PREMIUM)")
    parser.add_argument("--days", type=int, default=30,
                       help="License duration in days (default: 30)")
    parser.add_argument("--verify", type=str,
                       help="Verify a license key")
    parser.add_argument("--batch", type=int,
                       help="Generate multiple licenses")
    
    args = parser.parse_args()
    
    # Verify mode
    if args.verify:
        result = LicenseGenerator.verify(args.verify)
        print("\n" + "="*60)
        print("License Verification Result")
        print("="*60)
        print(f"License Key: {args.verify}")
        print(f"Valid: {result['valid']}")
        if result['valid']:
            print(f"Plan: {result['plan']}")
            print(f"Expiry: {result['expiry']}")
            print(f"Expired: {result['expired']}")
            print(f"Days Remaining: {result['days_remaining']}")
        else:
            print(f"Error: {result['error']}")
        print("="*60)
        return
    
    # Generate mode
    if args.batch:
        print("\n" + "="*60)
        print(f"Generating {args.batch} {args.plan} Licenses ({args.days} days)")
        print("="*60)
        for i in range(args.batch):
            license_key = LicenseGenerator.generate(args.plan, args.days)
            print(f"{i+1}. {license_key}")
        print("="*60)
    else:
        license_key = LicenseGenerator.generate(args.plan, args.days)
        
        print("\n" + "="*60)
        print("WoosAI License Key Generated")
        print("="*60)
        print(f"Plan: {args.plan}")
        print(f"Duration: {args.days} days")
        print(f"Expiry: {(datetime.now() + timedelta(days=args.days)).strftime('%Y-%m-%d')}")
        print()
        print(f"License Key:")
        print(f"  {license_key}")
        print()
        print("Usage:")
        print(f"  1. Save to .env file:")
        print(f"     WOOSAI_LICENSE={license_key}")
        print()
        print(f"  2. Or use in code:")
        print(f"     ai = WoosAI(license_key='{license_key}')")
        print("="*60)


if __name__ == "__main__":
    main()