import os


def generate_launch_files(state: dict) -> dict:
    files = {}
    checklist = f"""# {state['product_name']} Launch Checklist

## Pre-Launch (8 weeks before)
- [ ] Complete market research analysis
- [ ] Finalize product description and messaging
- [ ] Set pricing strategy
- [ ] Build landing page
- [ ] Create marketing materials
- [ ] Set up analytics tracking
- [ ] Prepare customer support resources

## Launch Week
- [ ] Execute marketing campaigns
- [ ] Monitor performance metrics
- [ ] Respond to customer feedback
- [ ] Track sales and conversions

## Post-Launch (8 weeks after)
- [ ] Analyze performance data
- [ ] Gather customer feedback
- [ ] Optimize based on learnings
- [ ] Plan next iteration

Generated on: {os.getcwd()}
"""
    files['launch_checklist.md'] = checklist

    calendar = f"""# {state['product_name']} Marketing Calendar

## Week 1-2: Pre-Launch Buzz
- Social media teasers
- Influencer outreach
- Email list building

## Week 3-4: Launch Preparation
- Press releases
- Partner announcements
- Final content creation

## Launch Week
- Launch announcement
- Social media campaigns
- Email marketing blast

## Post-Launch Weeks
- Customer testimonials
- Performance optimization
- Retargeting campaigns
"""
    files['marketing_calendar.md'] = calendar
    return files


