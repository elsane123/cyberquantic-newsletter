"""
CyberQuantic Weekly — Orchestrateur principal
Usage:
  python main.py                    # full run (test email)
  python main.py send               # send to all subscribers
  python main.py test you@email.com # test email only
  python main.py collect            # collector only
"""
import sys, logging
from agent1_collector import collect
from agent2_generator import generate
from agent3_publisher import publish

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger('main')

def run(mode='test', test_email=None):
    log.info('🚀 CyberQuantic Weekly — Starting pipeline...')
    ctx   = collect()
    draft = generate(ctx)
    result = publish(draft, test_email=test_email if mode in ('test','resend_test') else None)
    log.info(f"\n{'✅' if result.success else '❌'} Pipeline complete")
    log.info(f"  Emails sent     : {result.emails_sent}/{result.subscribers_count}")
    log.info(f"  Newsletter URL  : {result.newsletter_url}")
    log.info(f"  Blog URL        : {result.blog_url}")
    return result

if __name__ == '__main__':
    args = sys.argv[1:]
    mode = args[0] if args else 'test'
    if mode == 'collect':
        ctx = collect(); print(ctx.model_dump_json(indent=2))
    elif mode == 'test':
        email = args[1] if len(args) > 1 else 'elsane.tiberini@gmail.com'
        run('test', test_email=email)
    elif mode == 'send':
        run('send')
    else:
        run('test', test_email=mode)  # mode as email address
