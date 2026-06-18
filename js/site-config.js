/**
 * Safari & Bush Retreats - site contact & routing
 * Inquiries route to the Safari & Bush Retreats team (Ally Shebe, certified guide).
 */
(function () {
  'use strict';

  window.SITE_CONFIG = {
    businessName: 'Safari and Bush Retreats',
    contactName: 'Ally Shebe',
    email: 'info@safariandbushretreats.com',
    phoneDisplay: '+255 768 373 033',
    phoneTel: '+255768373033',
    whatsapp: '255768373033',
    whatsappText: "Hello, I'd like to plan a safari with Safari and Bush Retreats.",
    location: 'Tanzania - Nationwide',
    footerCredit: 'Tanzania-wide safari experts - real guides, real bush, no middlemen.',
    // FormSubmit.co - works on static hosting (no backend). Confirm email once after first submission.
    formSubmitEndpoint: 'https://formsubmit.co/ajax/info@safariandbushretreats.com'
  };

  window.siteWhatsAppUrl = function siteWhatsAppUrl(customText) {
    const text = encodeURIComponent(customText || window.SITE_CONFIG.whatsappText);
    return 'https://wa.me/' + window.SITE_CONFIG.whatsapp + '?text=' + text;
  };
})();
