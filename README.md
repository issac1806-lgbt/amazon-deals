# Issac's Picks

靜態 Amazon Associates 商品頁，站長是 Chun Hin（Issac）。每條商品連結都使用 `tag=issac03-20`。本站不編造折扣，也不顯示未經核對的價格。

A static Amazon Associates page run by Chun Hin (Issac). Every product link uses `tag=issac03-20`. The site does not invent discounts or show a price it has not verified.

## Regenerate the page

Edit `deals.json`, then rebuild `index.html`:

```bash
python3 generate_deals.py
```

Check that the committed page still matches the data file:

```bash
python3 generate_deals.py --check
```

The script uses only the Python standard library. It does not call an API, and it does not need a key.

Open `index.html` and switch language with 中文 / EN. A link can set it with `?lang=en` or `?lang=zh-Hant`. Category chips filter the list in the browser; they do not change the product links.

Each item in `deals.json` has:

| Field | Meaning |
| --- | --- |
| `title` | Product name, with `en` and `zh-Hant` |
| `asin` | The 10-character Amazon ASIN |
| `category` | Category label, with `en` and `zh-Hant` |
| `blurb` | What the product is, with `en` and `zh-Hant` |

Do not add a price or a discount. The generator rejects those fields, and it rejects a `%` in the copy. If a price cannot be checked at the moment someone reads the page, the page says to check Amazon.

`generate_deals.py` is the only generator. The old script hardcoded a third-party API key and made up percent-off badges. That file is gone. The key is still in older git history — revoke it at the provider so it cannot be reused.

## How the Associates tag works

Amazon Associates attributes a visit with a `tag` query parameter. This site links to:

```text
https://www.amazon.com/dp/ASIN?tag=issac03-20
```

`ASIN` is the product id from `deals.json`. The generator adds `?tag=issac03-20` when the product URL has no query string, and `&tag=issac03-20` when it already has one. The tag does not change the price a shopper pays.

A commission is possible only when all of these are true:

- The Associates account that owns `issac03-20` is approved.
- The shopper buys through that tagged link.
- The purchase qualifies under the current Associates Operating Agreement.

Amazon decides what qualifies. This repository cannot.

## Disclosure

The page earns commissions from qualifying purchases. `index.html` says so above the product list and again in the footer, in English and Traditional Chinese, including:

> As an Amazon Associate I earn from qualifying purchases.

## GitHub Pages

`index.html` is at the repository root, with a `.nojekyll` file so Pages serves it as a plain static site. In the repository settings, set Pages to deploy from the default branch and the `/` (root) folder. This repo does not include an analytics id.

## Next step: traffic

A correct tag earns nothing by itself. After the Associates account is approved and Pages is publishing this `index.html`, the remaining work is to send real visitors to the page. Commissions follow only if those visitors buy something that qualifies.
