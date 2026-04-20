/**
 * Reusable orange error alert (ChemClasify / Sistemas).
 * Expects markup from templates/Sistemas/fragmento_alerta_error.html
 */
(function () {
    'use strict';

    function overlayEl() {
        return document.getElementById('sistemas-alerta-error-overlay');
    }

    function textoEl() {
        return document.getElementById('sistemas-alerta-error-texto');
    }

    function botonCerrar() {
        return document.getElementById('sistemas-alerta-error-aceptar');
    }

    window.SistemasErrores = {
        mostrar: function (mensaje) {
            if (mensaje === null || mensaje === undefined || mensaje === '') {
                return;
            }
            var overlay = overlayEl();
            var texto = textoEl();
            if (!overlay || !texto) {
                return;
            }
            texto.textContent = String(mensaje);
            overlay.removeAttribute('hidden');
            overlay.setAttribute('aria-hidden', 'false');
            var btn = botonCerrar();
            if (btn) {
                btn.focus();
            }
        },

        cerrar: function () {
            var overlay = overlayEl();
            if (!overlay) {
                return;
            }
            overlay.setAttribute('hidden', 'hidden');
            overlay.setAttribute('aria-hidden', 'true');
        },
    };

    document.addEventListener('DOMContentLoaded', function () {
        var overlay = overlayEl();
        if (!overlay) {
            return;
        }
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                window.SistemasErrores.cerrar();
            }
        });
        var btn = botonCerrar();
        if (btn) {
            btn.addEventListener('click', function () {
                window.SistemasErrores.cerrar();
            });
        }

        // Server-rendered initial error: add in HTML (no Jinja inside .js files):
        // <script type="application/json" id="sistemas-error-inicial-json">...</script>
        var jsonEl = document.getElementById('sistemas-error-inicial-json');
        if (jsonEl && window.SistemasErrores) {
            var raw = (jsonEl.textContent || '').trim();
            if (raw) {
                try {
                    var inicial = JSON.parse(raw);
                    if (inicial !== null && inicial !== undefined && inicial !== '') {
                        window.SistemasErrores.mostrar(String(inicial));
                    }
                } catch (ignore) {
                    /* invalid payload */
                }
            }
        }
    });
})();
