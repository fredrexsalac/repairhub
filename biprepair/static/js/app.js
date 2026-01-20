document.addEventListener('DOMContentLoaded', () => {
    const bodyEl = document.body;
    const isClientAuthenticated = bodyEl?.dataset.clientAuthenticated === 'true';
    const gateRoot = document.querySelector('[data-client-gate-root]');
    const isAdminPath = window.location.pathname.startsWith('/admin');
    const installBanner = document.querySelector('[data-install-banner]');
    const installTrigger = installBanner?.querySelector('[data-install-trigger]');
    const installDismiss = installBanner?.querySelector('[data-install-dismiss]');
    const installCopyEl = installBanner?.querySelector('[data-install-copy]');
    let deferredPrompt = null;

    const policyModalLayer = document.querySelector('[data-policy-modal-layer]');
    const policyModalContent = policyModalLayer?.querySelector('[data-policy-modal-content]');
    const policyTemplateRoot = document.getElementById('policy-modal-library');

    const closeGate = (source = 'unknown') => {
        if (!gateRoot) return;
        console.debug('[client-gate] closing via', source);
        gateRoot.hidden = true;
        gateRoot.style.display = 'none';
        bodyEl?.classList.remove('modal-open');
    };

    const openGate = (source = 'unknown') => {
        if (!gateRoot) return;
        console.debug('[client-gate] opening via', source);
        gateRoot.hidden = false;
        gateRoot.style.display = 'grid';
        bodyEl?.classList.add('modal-open');
    };

    if (!isClientAuthenticated && gateRoot && !isAdminPath) {
        document.addEventListener('click', (event) => {
            const path = event.composedPath?.() || [];
            const targetEl = path.find((node) => node instanceof HTMLElement) || event.target;
            if (!(targetEl instanceof HTMLElement)) return;
            const dismissEl = targetEl.closest('[data-client-gate-dismiss], [data-admin-gate-dismiss]');
            if (dismissEl) {
                event.preventDefault();
                closeGate(dismissEl.dataset?.clientGateDismiss ?? 'dismiss-control');
                return;
            }

            const triggerEl = targetEl.closest('[data-client-gate-trigger]');
            if (triggerEl) {
                event.preventDefault();
                openGate(triggerEl.dataset?.clientGateTrigger ?? 'trigger-control');
            }
        });

        gateRoot.addEventListener('click', (event) => {
            if (event.target === gateRoot) {
                closeGate('scrim');
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && !gateRoot.hidden) {
                closeGate('escape-key');
            }
        });
    }

    if (gateRoot && isAdminPath) {
        gateRoot.hidden = true;
        gateRoot.style.display = 'none';
    }

    const initializeDisclaimers = () => {
        if (isClientAuthenticated) return;
        const banners = document.querySelectorAll('[data-disclaimer-banner]');
        if (!banners.length) return;
        banners.forEach((banner) => {
            if (!(banner instanceof HTMLElement)) return;
            const key = banner.dataset.disclaimerKey || 'biprepair_disclaimer';
            let storageAvailable = true;
            try {
                storageAvailable = typeof localStorage !== 'undefined';
            } catch (err) {
                storageAvailable = false;
            }
            if (storageAvailable && localStorage.getItem(key) === 'ack') {
                banner.remove();
                return;
            }
            const dismissBtn = banner.querySelector('[data-disclaimer-dismiss]');
            dismissBtn?.addEventListener('click', () => {
                if (storageAvailable) {
                    localStorage.setItem(key, 'ack');
                }
                banner.remove();
            });
        });
    };

    initializeDisclaimers();

    const initializeInstallBanner = () => {
        if (!installBanner) return;
        const isMobile = /iphone|ipad|android|mobile/i.test(navigator.userAgent);
        if (!isMobile) return;

        const appLabel = installBanner.dataset.installAppLabel || 'BiPSU Repair';
        if (installCopyEl) {
            installCopyEl.textContent = `Add ${appLabel} to your device for one-tap access.`;
        }

        const hideBanner = () => {
            installBanner.classList.remove('install-banner--visible');
            installBanner.hidden = true;
        };

        installDismiss?.addEventListener('click', () => {
            hideBanner();
            localStorage.setItem('biprepair_install_dismissed', 'true');
        });

        window.addEventListener('beforeinstallprompt', (event) => {
            event.preventDefault();
            if (localStorage.getItem('biprepair_install_dismissed') === 'true') return;
            deferredPrompt = event;
            installBanner.hidden = false;
            requestAnimationFrame(() => {
                installBanner.classList.add('install-banner--visible');
            });
        });

        installTrigger?.addEventListener('click', async () => {
            if (!deferredPrompt) return;
            deferredPrompt.prompt();
            const result = await deferredPrompt.userChoice;
            if (result.outcome === 'accepted') {
                localStorage.setItem('biprepair_install_dismissed', 'true');
                hideBanner();
            }
            deferredPrompt = null;
        });
    };

    initializeInstallBanner();

    const initializeLiveClock = () => {
        const targets = document.querySelectorAll('[data-live-clock]');
        if (!targets.length) return;
        const renderTime = () => {
            const nowPh = new Intl.DateTimeFormat('en-PH', {
                timeZone: 'Asia/Manila',
                dateStyle: 'medium',
                timeStyle: 'medium',
            }).format(new Date());
            targets.forEach((target) => {
                if (target instanceof HTMLElement) {
                    target.textContent = nowPh;
                    target.classList.remove('clock-tick');
                    void target.offsetWidth;
                    target.classList.add('clock-tick');
                }
            });
        };
        renderTime();
        setInterval(renderTime, 1000);
    };

    initializeLiveClock();

    const enhancePasswordFields = () => {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach((input) => {
            if (!(input instanceof HTMLInputElement)) return;
            if (input.dataset.passwordEnhanced === 'true') return;
            const wrapper = document.createElement('div');
            wrapper.className = 'password-wrapper';
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'password-toggle ghost';
            toggle.setAttribute('aria-label', 'Show password');
            toggle.textContent = 'Show';
            const parent = input.parentElement;
            if (!parent) return;
            parent.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            wrapper.appendChild(toggle);
            input.dataset.passwordEnhanced = 'true';

            toggle.addEventListener('click', () => {
                const isHidden = input.type === 'password';
                input.type = isHidden ? 'text' : 'password';
                toggle.textContent = isHidden ? 'Hide' : 'Show';
                toggle.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
            });
        });
    };

    enhancePasswordFields();

    const closePolicyModal = (source = 'unknown') => {
        if (!policyModalLayer) return;
        policyModalLayer.hidden = true;
        policyModalLayer.classList.remove('policy-modal-layer--open');
        bodyEl?.classList.remove('modal-open');
        console.debug('[policy-modal] closed via', source);
    };

    const openPolicyModal = (policy) => {
        if (!policyModalLayer || !policyModalContent || !policyTemplateRoot) return;
        if (!policy) return;
        const template = policyTemplateRoot.querySelector(`template[data-policy="${policy}"]`);
        if (!template) return;
        policyModalContent.innerHTML = template.innerHTML;
        policyModalLayer.hidden = false;
        policyModalLayer.classList.add('policy-modal-layer--open');
        bodyEl?.classList.add('modal-open');
        console.debug('[policy-modal] opened', policy);
    };

    document.addEventListener('click', (event) => {
        const path = event.composedPath?.() || [];
        const targetEl = path.find((node) => node instanceof HTMLElement) || event.target;
        if (!(targetEl instanceof HTMLElement)) return;

        const policyTrigger = targetEl.closest('[data-policy-modal-trigger]');
        if (policyTrigger) {
            event.preventDefault();
            event.stopPropagation();
            openPolicyModal(policyTrigger.dataset.policy);
            return;
        }

        const policyCloser = targetEl.closest('[data-policy-modal-close]');
        if (policyCloser) {
            event.preventDefault();
            closePolicyModal('button');
        }
    });

    policyModalLayer?.addEventListener('click', (event) => {
        if (event.target === policyModalLayer) {
            closePolicyModal('scrim');
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && policyModalLayer && !policyModalLayer.hidden) {
            closePolicyModal('escape');
        }
    });

    const form = document.getElementById('appointment-form');
    if (form) {
        const deviceField = form.querySelector('[name="device_type"]');
        const serviceField = form.querySelector('[name="service_type"]');
        const brandField = form.querySelector('[name="device_brand"]');
        const modelField = form.querySelector('[name="brand_model"]');
        const modelSuggestionBox = document.getElementById('model-suggestions');
        const brandSuggestionBox = document.getElementById('brand-suggestions');
        const issueField = form.querySelector('[name="issue_description"]');
        const warningBox = document.getElementById('service-warning');
        const warningText = warningBox?.querySelector('span');
        const serviceMap = JSON.parse(form.dataset.serviceMap || '{}');
        const brandMap = JSON.parse(form.dataset.brandMap || '{}');
        const modelMap = JSON.parse(form.dataset.modelMap || '{}');
        const servicePricingMap = JSON.parse(form.dataset.servicePricing || '{}');
        const priceCard = document.getElementById('service-price-card');
        const priceValueEl = document.getElementById('service-price-value');
        const paymentNoteEl = document.getElementById('service-payment-note');
        const servicePriceField = form.querySelector('[name="service_price"]') || form.appendChild((() => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'service_price';
            form.appendChild(input);
            return input;
        })());
        const gcashLinkEl = document.getElementById('gcash-contact-link');
        const paymentRadios = form.querySelectorAll('input[name="payment_method"]');
        const gcashContactUrl = form.dataset.gcashContact;
        const policyCheckbox =
            form.querySelector('input[type="checkbox"][name="accept_booking_policies"]') ||
            form.querySelector('.policy-checkbox-input');
        const policySubmitButton = form.querySelector('[data-policy-submit]');
        let currentBrandOptions = [];
        let currentModelSuggestions = [];
        const normalize = (value = '') => value.toLowerCase().replace(/\s+/g, ' ').trim();

        const formatCurrency = (value) =>
            new Intl.NumberFormat('en-PH', {
                style: 'currency',
                currency: 'PHP',
                maximumFractionDigits: 0,
            }).format(value);

        const updateServicePrice = () => {
            if (!priceCard || !serviceField || !deviceField) return;
            const devicePricing = servicePricingMap[deviceField.value] || {};
            const price = devicePricing[serviceField.value];
            if (price && priceValueEl && paymentNoteEl) {
                priceValueEl.textContent = formatCurrency(price);
                paymentNoteEl.textContent = `Payment through cash or GCash after onsite diagnostics. Estimated total: ${formatCurrency(
                    price,
                )}.`;
                if (servicePriceField) {
                    servicePriceField.value = price;
                }
            } else if (priceValueEl && paymentNoteEl) {
                priceValueEl.textContent = 'Select a service to preview cost';
                paymentNoteEl.textContent = 'Payment through cash or GCash after onsite diagnostics.';
                if (servicePriceField) {
                    servicePriceField.value = '';
                }
            }
        };

        const updatePaymentWidgets = () => {
            if (!paymentNoteEl) return;
            const selected = Array.from(paymentRadios).find((radio) => radio.checked);
            const method = selected?.value || 'personal';
            if (method === 'gcash') {
                paymentNoteEl.textContent = 'We will send the GCash QR via Messenger before the meetup.';
                if (gcashLinkEl) {
                    gcashLinkEl.hidden = false;
                    if (gcashContactUrl) {
                        gcashLinkEl.href = gcashContactUrl;
                    }
                }
            } else {
                paymentNoteEl.textContent = 'Bring exact cash for onsite payment after diagnostics.';
                if (gcashLinkEl) {
                    gcashLinkEl.hidden = true;
                }
            }
        };

        const renderServices = () => {
            const device = deviceField.value;
            const options = serviceMap[device] || [];
            serviceField.innerHTML = '';
            options.forEach(({ value, label }) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = label;
                serviceField.appendChild(option);
            });
            updateServicePrice();
        };

        const findBrandSlug = (input = '') => {
            const normalized = normalize(input);
            if (!normalized) return null;
            const exact =
                currentBrandOptions.find(
                    ({ value, label }) =>
                        normalize(value) === normalized || normalize(label) === normalized
                ) || null;
            if (exact) return exact.value;
            const partial =
                currentBrandOptions.find(
                    ({ value, label }) =>
                        normalize(label).includes(normalized) || normalize(value).includes(normalized)
                ) || null;
            return partial?.value || null;
        };

        const renderBrands = () => {
            if (!brandField) return;
            const device = deviceField.value;
            if (device === 'iphone') {
                brandField.value = 'Apple';
                brandField.setAttribute('readonly', 'readonly');
                brandSuggestionBox?.setAttribute('hidden', 'hidden');
            } else {
                brandField.removeAttribute('readonly');
            }
            currentBrandOptions = brandMap[device] || [];
            updateBrandSuggestionBox(brandField.value || '');
            renderModels();
        };

        const renderModels = () => {
            if (!modelField) return;
            const device = deviceField.value;
            let brandSlug = findBrandSlug(brandField?.value) || null;
            if (device === 'iphone') {
                brandSlug = 'apple';
            } else if (!brandSlug && currentBrandOptions.length) {
                brandSlug = currentBrandOptions[0].value;
            }
            currentModelSuggestions =
                (modelMap[device] && brandSlug ? modelMap[device][brandSlug] : []) || [];
            updateModelSuggestionBox(modelField.value || '');
        };

        const updateModelSuggestionBox = (query = '') => {
            if (!modelSuggestionBox) return;
            const normalized = query.toLowerCase();
            const filtered = currentModelSuggestions.filter((item) =>
                item.toLowerCase().includes(normalized)
            );
            modelSuggestionBox.innerHTML = '';
            if (!filtered.length) {
                modelSuggestionBox.hidden = true;
                return;
            }
            filtered.slice(0, 8).forEach((item) => {
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = item;
                button.className = 'suggestion-pill';
                button.dataset.value = item;
                modelSuggestionBox.appendChild(button);
            });
            modelSuggestionBox.hidden = false;
        };

        const updateBrandSuggestionBox = (query = '') => {
            if (!brandSuggestionBox || !brandField) return;
            if (brandField.hasAttribute('readonly')) {
                brandSuggestionBox.hidden = true;
                return;
            }
            const normalized = normalize(query);
            const filtered = currentBrandOptions.filter(
                ({ value, label }) =>
                    !normalized ||
                    normalize(label).includes(normalized) ||
                    normalize(value).includes(normalized)
            );
            brandSuggestionBox.innerHTML = '';
            if (!filtered.length) {
                brandSuggestionBox.hidden = true;
                return;
            }
            filtered.slice(0, 6).forEach(({ value, label }) => {
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = label;
                button.className = 'suggestion-pill';
                button.dataset.slug = value;
                brandSuggestionBox.appendChild(button);
            });
            brandSuggestionBox.hidden = false;
        };

        const evaluateWarnings = () => {
            if (!warningBox) return;
            const device = deviceField.value;
            const issue = (issueField.value || '').toLowerCase();
            const blockedKeywords = ['solder', 'motherboard', 'board level'];
            const batteryMention = issue.includes('battery');

            let message = '';
            if (device === 'iphone' && batteryMention) {
                message = 'We decline iPhone battery cases. Please consider an authorized service center.';
            } else if (blockedKeywords.some((k) => issue.includes(k))) {
                message = 'Board-level or soldering work is unsafe for field repairs. We cannot accept this job.';
            }

            if (message) {
                warningText.textContent = message;
                warningBox.hidden = false;
            } else {
                warningBox.hidden = true;
            }
        };

        const syncPolicySubmitState = () => {
            if (!policySubmitButton) return;
            const consentGiven = policyCheckbox?.checked === true;
            const isAllowed = consentGiven;
            policySubmitButton.disabled = !isAllowed;
            if (isAllowed) {
                policySubmitButton.removeAttribute('disabled');
            } else {
                policySubmitButton.setAttribute('disabled', 'disabled');
            }
            policySubmitButton.setAttribute('aria-disabled', String(!isAllowed));
            policySubmitButton.classList.toggle('btn--disabled', !isAllowed);
            policySubmitButton.classList.toggle('btn--ready', isAllowed);
        };

        policyCheckbox?.addEventListener('change', syncPolicySubmitState);
        syncPolicySubmitState();

        brandField?.addEventListener('input', () => {
            updateBrandSuggestionBox(brandField.value);
        });
        deviceField?.addEventListener('change', () => {
            renderServices();
            renderBrands();
        });
        serviceField?.addEventListener('change', () => {
            updateServicePrice();
        });
        brandField?.addEventListener('focus', () => {
            updateBrandSuggestionBox(brandField.value);
        });
        brandField?.addEventListener('blur', () => {
            setTimeout(() => {
                if (brandSuggestionBox) brandSuggestionBox.hidden = true;
            }, 150);
        });
        brandSuggestionBox?.addEventListener('mousedown', (event) => {
            if (!(event.target instanceof HTMLButtonElement)) return;
            const label = event.target.textContent;
            if (!label || !brandField) return;
            event.preventDefault();
            brandField.value = label;
            brandSuggestionBox.hidden = true;
            renderModels();
        });

        modelField?.addEventListener('input', (event) => {
            updateModelSuggestionBox(event.target.value);
        });
        modelSuggestionBox?.addEventListener('mousedown', (event) => {
            if (!(event.target instanceof HTMLButtonElement)) return;
            const value = event.target.dataset.value;
            if (!value || !modelField) return;
            event.preventDefault();
            modelField.value = value;
            modelSuggestionBox.hidden = true;
        });
        modelField?.addEventListener('blur', () => {
            setTimeout(() => {
                if (modelSuggestionBox) modelSuggestionBox.hidden = true;
            }, 150);
        });
        modelField?.addEventListener('focus', () => {
            updateModelSuggestionBox(modelField.value || '');
        });
        issueField?.addEventListener('input', evaluateWarnings);

        renderServices();
        renderBrands();
        updateServicePrice();
        updatePaymentWidgets();
        evaluateWarnings();
    }

    const initializeContactMessenger = () => {
        const threadEl = document.querySelector('[data-contact-thread]');
        const composerForm = document.querySelector('[data-contact-composer]');
        if (!threadEl || !(threadEl instanceof HTMLElement)) return;
        const historyUrl = threadEl.dataset.historyUrl;
        if (!historyUrl) return;
        const clientInitials = threadEl.dataset.clientInitials || 'You';
        const clientName = threadEl.dataset.clientName || 'You';
        let adminInitials = threadEl.dataset.adminInitials || 'RC';
        let adminName = threadEl.dataset.adminName || 'Repair Crew';
        const emptyTitle = threadEl.dataset.emptyTitle || 'No messages yet';
        const emptyBody = threadEl.dataset.emptyBody || '';
        let lastSignature = '';
        let pollTimer = null;

        const createBubble = (type, options) => {
            const article = document.createElement('article');
            article.className = `bubble bubble--${type}`;
            const avatar = document.createElement('div');
            avatar.className = 'bubble__avatar';
            avatar.setAttribute('aria-hidden', 'true');
            avatar.textContent = options.initials;
            const body = document.createElement('div');
            body.className = 'bubble__body';
            const meta = document.createElement('div');
            meta.className = 'bubble__meta';
            const nameEl = document.createElement('strong');
            nameEl.textContent = options.name;
            const timeEl = document.createElement('small');
            timeEl.textContent = options.timestamp;
            meta.appendChild(nameEl);
            meta.appendChild(timeEl);
            body.appendChild(meta);
            if (options.subject) {
                const subjectEl = document.createElement('p');
                subjectEl.className = 'bubble__subject';
                subjectEl.textContent = options.subject;
                body.appendChild(subjectEl);
            }
            const messageEl = document.createElement('p');
            messageEl.textContent = options.body;
            body.appendChild(messageEl);
            if (options.footer) {
                const footer = document.createElement('div');
                footer.className = 'bubble__footer';
                options.footer.forEach((text) => {
                    const small = document.createElement('small');
                    small.textContent = text;
                    footer.appendChild(small);
                });
                body.appendChild(footer);
            }
            article.appendChild(avatar);
            article.appendChild(body);
            return article;
        };

        const renderThread = (messages, adminMeta) => {
            threadEl.innerHTML = '';
            if (!messages.length) {
                const emptyState = document.createElement('div');
                emptyState.className = 'messenger-empty';
                const title = document.createElement('p');
                title.className = 'messenger-empty__title';
                title.textContent = emptyTitle;
                const body = document.createElement('p');
                body.textContent = emptyBody;
                emptyState.appendChild(title);
                emptyState.appendChild(body);
                threadEl.appendChild(emptyState);
                return;
            }

            if (adminMeta) {
                adminInitials = adminMeta.initials || adminInitials;
                adminName = adminMeta.name || adminName;
            }

            const frag = document.createDocumentFragment();
            messages.forEach((message) => {
                frag.appendChild(
                    createBubble('client', {
                        initials: clientInitials,
                        name: clientName,
                        timestamp: message.created_display,
                        subject: message.subject,
                        body: message.body,
                        footer: [
                            `${message.status_display}`,
                            message.preferred_contact_display,
                        ],
                    }),
                );
                if (message.admin_reply) {
                    frag.appendChild(
                        createBubble('admin', {
                            initials: adminInitials,
                            name: adminName,
                            timestamp: message.updated_display,
                            body: message.admin_reply,
                        }),
                    );
                }
            });
            threadEl.appendChild(frag);
            threadEl.scrollTop = threadEl.scrollHeight;
        };

        const fetchMessages = async () => {
            try {
                const response = await fetch(historyUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                if (!response.ok) throw new Error(`History request failed: ${response.status}`);
                const data = await response.json();
                const signature = JSON.stringify(
                    data.messages.map((msg) => `${msg.id}-${msg.updated_iso}-${msg.admin_reply || ''}`),
                );
                if (signature === lastSignature) return;
                lastSignature = signature;
                renderThread(data.messages || [], data.admin || {});
            } catch (error) {
                console.error('[contact-admin] Unable to refresh thread', error);
            }
        };

        const startPolling = () => {
            fetchMessages();
            pollTimer = setInterval(fetchMessages, 6000);
        };

        const stopPolling = () => {
            if (pollTimer) {
                clearInterval(pollTimer);
                pollTimer = null;
            }
        };

        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                startPolling();
            } else {
                stopPolling();
            }
        });

        composerForm?.addEventListener('submit', () => {
            stopPolling();
        });

        startPolling();
    };

    initializeContactMessenger();
});
