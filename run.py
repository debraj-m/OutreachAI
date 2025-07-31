"""
Command Line Interface for Personalized Email Automation
========================================================

Simple CLI to run the email automation system.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from email_automation.main import PersonalizedEmailAutomation


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Personalized Email Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py prospects.csv --test-mode
  python run.py prospects.csv --output results.json
  python run.py prospects.csv --delay 60 --test-email
        """
    )
    
    parser.add_argument(
        'csv_file',
        help='Path to CSV file containing prospect data'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode (no emails sent)'
    )
    
    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Test email connection before starting'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for results (JSON format)'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=30,
        help='Delay between prospects in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file (.env)'
    )
    
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Only show statistics, don\'t process prospects'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize automation system
        print("Initializing Personalized Email Automation...")
        automation = PersonalizedEmailAutomation(args.config)
        
        # Test email connection if requested
        if args.test_email:
            print("Testing email connection...")
            if not automation.test_email_connection():
                print("❌ Email connection test failed. Please check your configuration.")
                return 1
            print("✅ Email connection test successful!")
        
        # Load prospects
        print(f"Loading prospects from {args.csv_file}...")
        if not automation.load_prospects(args.csv_file):
            print("❌ Failed to load prospects. Please check your CSV file.")
            return 1
        
        print(f"✅ Loaded {len(automation.prospects)} prospects successfully!")
        
        # Show stats if requested
        if args.stats_only:
            stats = automation.prospect_manager.get_stats()
            print("\n=== PROSPECT STATISTICS ===")
            for key, value in stats.items():
                print(f"{key}: {value}")
            return 0
        
        # Confirmation prompt
        if not args.test_mode:
            response = input(f"\nReady to send {len(automation.prospects)} emails. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return 0
        
        # Process prospects
        print(f"\nStarting processing...")
        if args.test_mode:
            print("🧪 TEST MODE: No emails will be sent")
        
        results = automation.process_all_prospects(
            test_mode=args.test_mode,
            delay_between_prospects=args.delay
        )
        
        # Show final statistics
        stats = automation.get_statistics()
        print("\n=== FINAL RESULTS ===")
        print(f"Total prospects: {stats['total_prospects']}")
        print(f"Successfully processed: {stats['successful_processing']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Average personalization score: {stats['average_personalization_score']:.2f}")
        
        if not args.test_mode and stats['email_delivery_stats']['total_emails'] > 0:
            delivery_stats = stats['email_delivery_stats']
            print(f"Email delivery success rate: {delivery_stats['success_rate']:.1f}%")
        
        # Export results if requested
        if args.output:
            if automation.export_results(args.output):
                print(f"✅ Results exported to {args.output}")
            else:
                print(f"❌ Failed to export results to {args.output}")
        
        print("\n✅ Processing completed!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
