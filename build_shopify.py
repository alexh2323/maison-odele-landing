# Landing GitHub Pages -> corps de page Shopify (thème Horizon) pour femme / fille / garcon.
# CSS limité à #mo, images base64 -> img/<hash> servies par GitHub Pages, formulaire -> clients Shopify (tag liste-attente-bf).
import re, os, sys, base64, hashlib
R = os.path.dirname(os.path.abspath(__file__)); BASE = 'https://alexh2323.github.io/maison-odele-landing/img/'
SRC = {'femme': 'index.html', 'fille': 'fille/index.html', 'garcon': 'garcon/index.html'}
INTEG = open(f'{R}/shopify_femme_body.html').read()
INTEG = INTEG[INTEG.index('/* intégration Shopify'):INTEG.index('</style>')]   # masque en-tête/pied du thème, pleine largeur

def scope_sel(sel):
    sel = sel.strip()
    if sel in (':root', 'html', 'body', 'html,body'): return '#mo'
    for p in ('html ', 'body '):
        if sel.startswith(p): return '#mo ' + sel[len(p):]
    return '#mo ' + sel
def scope(css):
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0: out.append(css[i:]); break
        head = css[i:j]; k, d = j + 1, 1
        while d: d += {'{': 1, '}': -1}.get(css[k], 0); k += 1
        inner = css[j + 1:k - 1]; h = head.strip()
        com = re.match(r'(\s*(?:/\*.*?\*/\s*)*)', head, re.S).group(1); h = head[len(com):].strip()
        if h.startswith('@keyframes') or h.startswith('@font-face'): out.append(head + '{' + inner + '}')
        elif h.startswith('@'): out.append(com + h + '{' + scope(inner) + '}')
        else: out.append(com + ','.join(scope_sel(x) for x in h.split(',')) + '{' + inner + '}')
        i = k
    return ''.join(out)
def img(m):
    ext = {'jpeg': 'jpg', 'png': 'png', 'webp': 'webp'}[m.group(1)]; raw = base64.b64decode(m.group(2))
    name = hashlib.sha1(raw).hexdigest()[:12] + '.' + ext; p = f'{R}/img/{name}'
    if not os.path.exists(p): open(p, 'wb').write(raw)
    return BASE + name
def build(g):
    s = open(f'{R}/{SRC[g]}').read()
    css = s[s.index('<style>') + 7:s.index('</style>')]
    body = s[s.index('>', s.index('<body')) + 1:s.index('</body>')]
    body = re.sub(r'data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)', img, body)
    css = re.sub(r'data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)', img, css)
    body = body.replace('<form id="f" novalidate>', '<form id="f" method="post" action="/contact#f" accept-charset="UTF-8" novalidate><input type="hidden" name="form_type" value="customer"><input type="hidden" name="utf8" value="✓"><input type="hidden" name="contact[tags]" value="liste-attente-bf,newsletter,' + g + '">')
    body = body.replace('<input id="email" name="email"', '<input id="email" name="contact[email]"')
    a = "  e.preventDefault();\n"; assert a in body; body = body.replace(a, '')
    a = "if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(em.value)){em.setAttribute('aria-invalid','true');em.focus();return}"
    assert a in body, 'validation email introuvable'; body = body.replace(a, "if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(em.value)){e.preventDefault();em.setAttribute('aria-invalid','true');em.focus();return}")
    a = "  document.getElementById('go').hidden=true;document.getElementById('ok').hidden=false;\n"; assert a in body
    body = body.replace(a, "  document.getElementById('go').disabled=true;\n")
    k = body.rindex('</script>')
    body = body[:k] + "(function(){var q=location.search;if(q.indexOf('customer_posted=true')<0&&q.indexOf('contact%5Bemail%5D')<0)return;\ndocument.getElementById('go').hidden=true;document.getElementById('ok').hidden=false;document.getElementById('f').scrollIntoView({block:'center'})})();\n" + body[k:]
    head = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Montserrat:wght@600&display=swap">\n'
    reset = '#mo *{box-sizing:border-box}#mo h1,#mo h2,#mo h3,#mo p,#mo button,#mo label{letter-spacing:normal;text-transform:none}\n'
    integ = INTEG.replace(reset.strip(), '')   # le reset du theme passe AVANT le CSS de la page, sinon il efface les majuscules du titre
    out = head + '<style>\n' + reset + scope(css) + '\n' + integ + '</style>\n<div id="mo">\n' + body.strip() + '\n</div>\n'
    assert not re.search(r'data:image/(jpeg|png|webp)', out)
    open(f'{R}/shopify_{g}_body.html', 'w').write(out); return len(out)
if __name__ == '__main__':
    for g in (sys.argv[1:] or SRC): print(g, build(g), 'octets')
