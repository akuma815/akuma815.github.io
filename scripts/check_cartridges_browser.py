"""Optional real-browser QA. Run a local server first; see README for setup."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--channel', default='chromium', help='chromium or an installed msedge/chrome')
    args = parser.parse_args()
    output = ROOT / 'qa/cartridges'
    output.mkdir(parents=True, exist_ok=True)
    errors = []
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel=None if args.channel == 'chromium' else args.channel)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        expect(page.locator('.pack-pick')).to_have_count(20)
        # Decode offscreen lazy images explicitly for the asset check and captures.
        page.locator('.pack-art img').evaluate_all('(images) => Promise.all(images.map(i => { i.loading = "eager"; return i.decode(); }))')
        assert page.locator('.pack-art img').evaluate_all('(images) => images.every(i => i.complete && i.naturalWidth > 0)')
        for width in [1440, 1024, 768, 390, 320]:
            page.set_viewport_size({'width': width, 'height': 1000})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'horizontal overflow at {width}px'
        checks.append('20 labelled packs; captures load; no page overflow at 320/390/768/1024/1440px')
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.locator('#games').evaluate('(el) => window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 40)')
        page.screenshot(path=str(output / 'desktop-shelf.png'))
        first = page.locator('.pack-pick').first
        first.focus()
        page.keyboard.press('Enter')
        expect(page.locator('#details')).to_have_attribute('data-loading', 'true')
        expect(page.locator('#game-introduction')).to_be_hidden()
        start = page.locator('#insert-pack').evaluate('(el) => el.getBoundingClientRect().top')
        page.screenshot(path=str(output / 'insertion.png'))
        page.wait_for_timeout(650)
        end = page.locator('#insert-pack').evaluate('(el) => el.getBoundingClientRect().top')
        assert end > start + 35, 'selected pack did not move into the console'
        expect(page.locator('#game-introduction')).to_be_visible()
        expect(page.locator('#details')).to_have_attribute('data-loading', 'false')
        expect(page.locator('#dialog-media img')).to_be_visible()
        page.locator('#game-introduction').evaluate('(el) => Promise.all(el.getAnimations().map(a => a.finished))')
        page.screenshot(path=str(output / 'desktop-introduction.png'))
        page.keyboard.press('Escape')
        expect(page.locator('#details')).not_to_be_visible()
        expect(first).to_be_focused()
        checks.append('keyboard selection; real insertion movement; introduction reveal; Escape restores focus')
        # Closing early must not let a late timer reopen or reveal an old game.
        first.click()
        page.keyboard.press('Escape')
        page.wait_for_timeout(1200)
        expect(page.locator('#details')).not_to_be_visible()
        expect(page.locator('#game-introduction')).to_be_hidden()
        checks.append('Escape during insertion cancels the pending reveal')
        first.click()
        page.keyboard.press('Tab')
        expect(page.locator('#skip-insert')).to_be_focused()
        page.keyboard.press('Enter')
        expect(page.locator('#game-introduction')).to_be_visible()
        expect(page.locator('#close-dialog')).to_be_focused()
        page.locator('#close-dialog').click()
        checks.append('skip by keyboard; focus moves from hidden skip button to visible close button')
        context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, reduced_motion='no-preference')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        first = page.locator('.pack-pick').first
        page.locator('#games').evaluate('(el) => window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 25)')
        page.screenshot(path=str(output / 'mobile-shelf.png'))
        # Exercise a different physical media shape on a narrow viewport.
        umd = page.locator('.pack-pick').filter(has=page.locator('.media-umd')).first
        umd.click()
        expect(page.locator('#insert-pack .media-umd')).to_have_count(1)
        page.locator('#skip-insert').click()
        expect(page.locator('#dialog-title')).to_be_visible()
        assert page.locator('#details').evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'dialog overflow'
        page.locator('#game-introduction').evaluate('(el) => Promise.all(el.getAnimations().map(a => a.finished))')
        page.screenshot(path=str(output / 'mobile-introduction.png'))
        page.keyboard.press('Escape')
        expect(umd).to_be_focused()
        checks.append('mobile UMD selection; matching pack; skip; introduction fits narrow dialog')
        page.emulate_media(reduced_motion='reduce')
        first.click()
        expect(page.locator('#details')).to_have_attribute('data-loading', 'false')
        expect(page.locator('#game-introduction')).to_be_visible()
        expect(page.locator('#insert-stage')).to_be_hidden()
        page.keyboard.press('Escape')
        checks.append('reduced-motion setting opens introduction without waiting or insertion')
        assert not errors, errors
        browser.close()
    result = dict(status='PASS',browser_channel=args.channel,url=args.url,checks=checks,page_errors=errors)
    (output / 'browser_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
