(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];

  /* Menu mobile */
  const toggle = $('.nav-toggle'), menu = $('#menu');
  const closeMenu = () => { menu.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); toggle.setAttribute('aria-label', 'Abrir menu'); };
  toggle.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });

  /* Rolagem suave por âncoras (na home); em outras páginas segue o link normal */
  document.addEventListener('click', e => {
    const a = e.target.closest('[data-scroll]');
    if (!a || location.pathname !== '/') return;
    e.preventDefault();
    const id = a.dataset.scroll;
    if (id === 'inicio') window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
    else document.getElementById(id)?.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth' });
    history.replaceState(null, '', id === 'inicio' ? '/' : '#' + id);
    closeMenu();
    if (a.dataset.servico) selecionarServico(a.dataset.servico);
  });
  function selecionarServico(nome) {
    const sel = $('#ag-tipo'); if (!sel) return;
    [...sel.options].forEach(o => { if (o.value === nome) sel.value = nome; });
  }

  /* Link ativo no menu */
  const links = $$('.nav a[data-scroll]:not(.btn)');
  if ('IntersectionObserver' in window && location.pathname === '/') {
    const spy = new IntersectionObserver(es => es.forEach(en => {
      if (!en.isIntersecting) return;
      links.forEach(l => l.classList.toggle('active', l.dataset.scroll === en.target.id));
    }), { rootMargin: '-45% 0px -50% 0px' });
    ['inicio', 'agendamento', 'contato', 'precos', 'blog'].forEach(id => { const el = document.getElementById(id); if (el) spy.observe(el); });
  }

  /* Aparecer ao rolar */
  const rev = $$('.reveal');
  if ('IntersectionObserver' in window && !reduced) {
    const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); } }), { threshold: .12 });
    rev.forEach(el => io.observe(el));
  } else rev.forEach(el => el.classList.add('visible'));

  /* Carrossel de preços: desliza para o lado e avança sozinho */
  const ring = $('#ring');
  if (ring) {
    const box = $('#carousel'), originais = [...ring.children], n = originais.length;
    const GAP = 24, DUR = 700;
    let pv = 1, idx = 0, step = 0, timer = null, busy = false, startX = null, resizeT;
    const perView = () => innerWidth >= 1000 ? 3 : innerWidth >= 640 ? 2 : 1;
    const move = animar => { ring.style.transition = animar ? '' : 'none'; ring.style.transform = `translateX(${-idx * step}px)`; };
    function build() {
      ring.querySelectorAll('.clone').forEach(c => c.remove());
      pv = perView(); idx = 0; busy = false;
      const cw = (ring.clientWidth - GAP * (pv - 1)) / pv; step = cw + GAP;
      const flat = n <= pv; box.classList.toggle('is-flat', flat);
      if (!flat) originais.slice(0, pv).forEach(c => {
        const k = c.cloneNode(true); k.classList.add('clone'); k.setAttribute('aria-hidden', 'true'); k.setAttribute('inert', ''); ring.appendChild(k);
      });
      [...ring.children].forEach((c, i, all) => { c.style.width = cw + 'px'; c.style.marginRight = i < all.length - 1 ? GAP + 'px' : '0'; });
      move(false); restart();
    }
    const settle = () => { if (idx >= n) { idx = 0; move(false); } busy = false; };
    function next() { if (busy || n <= pv) return; busy = true; idx++; move(true); setTimeout(settle, DUR + 40); }
    function prev() {
      if (busy || n <= pv) return; busy = true;
      if (idx === 0) { idx = n; move(false); ring.getBoundingClientRect(); }
      idx--; move(true); setTimeout(settle, DUR + 40);
    }
    function restart() { clearInterval(timer); if (!reduced && n > pv) timer = setInterval(next, 4000); }
    $('#prev').addEventListener('click', () => { prev(); restart(); });
    $('#next').addEventListener('click', () => { next(); restart(); });
    box.addEventListener('mouseenter', () => clearInterval(timer));
    box.addEventListener('mouseleave', restart);
    box.addEventListener('focusin', () => clearInterval(timer));
    box.addEventListener('focusout', restart);
    box.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') prev(); if (e.key === 'ArrowRight') next(); });
    box.addEventListener('pointerdown', e => { startX = e.clientX; });
    box.addEventListener('pointerup', e => { if (startX === null) return; const dx = e.clientX - startX; if (Math.abs(dx) > 40) { dx < 0 ? next() : prev(); restart(); } startX = null; });
    addEventListener('resize', () => { clearTimeout(resizeT); resizeT = setTimeout(build, 200); });
    build();
  }

  /* Formulário de agendamento */
  const form = $('#form-agendamento');
  if (form) {
    const status = $('#ag-status'), btn = $('#ag-enviar'), data = $('#ag-data');
    const hoje = new Date(); hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset());
    data.min = hoje.toISOString().slice(0, 10);
    const erro = (campo, msg) => {
      const el = $(`.err[data-for="${campo}"]`, form), inp = form.elements[campo];
      if (el) el.textContent = msg || ''; if (inp) inp.setAttribute('aria-invalid', msg ? 'true' : 'false');
    };
    const validar = () => {
      let ok = true; const v = n => form.elements[n].value.trim();
      const regras = {
        nome: v('nome').length < 3 && 'Informe seu nome completo.',
        email: !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v('email')) && 'Informe um e-mail válido.',
        telefone: !/^[0-9()+\-\s]{8,20}$/.test(v('telefone')) && 'Informe um telefone válido.',
        data: (!v('data') || v('data') < data.min) && 'Escolha uma data a partir de hoje.',
        horario: !v('horario') && 'Escolha um horário.',
        tipo: !v('tipo') && 'Escolha o tipo de atendimento.'
      };
      Object.entries(regras).forEach(([c, m]) => { erro(c, m || ''); if (m) ok = false; });
      return ok;
    };
    form.addEventListener('submit', async e => {
      e.preventDefault(); status.className = 'status'; status.textContent = '';
      if (!validar()) { status.className = 'status fail'; status.textContent = 'Revise os campos destacados.'; return; }
      const payload = Object.fromEntries(new FormData(form).entries());
      const token = $('meta[name="_csrf"]').content, header = $('meta[name="_csrf_header"]').content;
      btn.disabled = true; btn.textContent = 'Enviando...';
      try {
        const res = await fetch('/api/agendamento', { method: 'POST', headers: { 'Content-Type': 'application/json', [header]: token }, body: JSON.stringify(payload) });
        const json = await res.json().catch(() => ({}));
        if (res.ok) { form.reset(); status.className = 'status ok'; status.textContent = json.message; }
        else {
          if (json.erros) Object.entries(json.erros).forEach(([c, m]) => erro(c, m));
          status.className = 'status fail'; status.textContent = json.message || 'Não foi possível enviar. Tente novamente.';
        }
      } catch { status.className = 'status fail'; status.textContent = 'Sem conexão. Verifique a internet e tente novamente.'; }
      finally { btn.disabled = false; btn.textContent = 'Solicitar Agendamento'; }
    });
  }
})();
