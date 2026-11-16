export type Language = 'tr' | 'en';

export const translations = {
  tr: {
    // Header
    newComparison: 'Yeni Karşılaştırma',
    modelsActive: 'Model Aktif',
    nvidiaLive: 'NVIDIA Canlı',
    noApiKey: 'API Key Eksik',
    changeLanguage: 'Switch to English',
    langLabel: 'EN',

    // Sidebar
    conversations: 'Karşılaştırmalar',
    newChat: 'Yeni Karşılaştırma',
    noChats: 'Henüz kayıtlı oturum yok.',
    noChatsDesc: 'Bir soru sorarak çoklu model karşılaştırması başlatın.',
    deleteConfirm: 'Bu oturumu silmek istediğinizden emin misiniz?',
    today: 'Bugün',
    yesterday: 'Dün',
    older: 'Daha Eski',

    // Empty State
    heroTitle: 'Tek Soru. Çoklu Zihin.',
    heroSubtitle: 'Yapay zeka modellerinin mimarilerini, akıl yürütme adımlarını, devre çözümlerini ve hızlarını yan yana canlı olarak test edin.',
    quickPresets: 'Hızlı Testler',
    presetCoding: 'Kodlama & Refactor',
    presetMath: 'Matematik & Mantık',
    presetCircuit: 'Devre & Görsel Analiz',
    presetSpeed: 'Hızlı Özetleme',
    presetFrontier: 'Frontier Derin Sentez',
    promptPlaceholderExample: 'Örnek bir soru deneyin:',
    exampleCoding: 'Python asyncio ile semaphore ve backoff içeren bir kuyruk worker yaz.',
    exampleMath: '2^(2x) - 3 * 2^(x+2) + 32 = 0 denklemini adımlı çöz.',
    exampleCircuit: 'Ekli PDF şemasındaki diyot ve transistör devrelerinde Vo gerilimini ve akımları hesapla.',

    // ChatInput
    inputPlaceholder: 'Bir soru sorun veya fotoğraf/belge yükleyin (PDF, Görsel, Python, JSON)...',
    inputPlaceholderDocs: 'Eklenen devre şeması / belgeler hakkında ne hesaplamak istersiniz?',
    systemToggle: 'Sistem Talimatı',
    systemPlaceholder: 'Örn: Devre analizinde tüm Kirchoff adımlarını ve formüllerini açıkça göster.',
    modelsLabel: 'Modeller',
    changeModels: 'Değiştir',
    systemBtn: 'Talimat',
    sendBtn: 'Modellere Gönder',
    dropHint: 'Fotoğraf, PDF veya kod dosyalarını sürükleyip bırakabilirsiniz',
    uploadingHint: 'Belge ve şemalar ayrıştırılıyor...',
    visionRecommend: 'Devre şeması veya çizimleri incelemek için Görsel (Vision) modeli önerilir:',
    addVisionModel: '+ Nemotron Super VL Ekle',
    footerInfo: 'NVIDIA Build NIM Çoklu Model Altyapısı',

    // Comparison Card & Grid
    perspectives: 'Eşzamanlı Model Karşılaştırması',
    copy: 'Kopyala',
    copied: 'Kopyalandı!',
    retry: 'Yeniden Dene',
    retrying: 'Yeniden deneniyor...',
    reasoningProcess: '🧠 Çıkarım & Devre Analizi Süreci',
    hideReasoning: 'Analiz Adımlarını Gizle',
    showReasoning: 'Analiz Adımlarını Göster',
    finalAnswer: '⚡ Çözüm ve Sonuç',
    latency: 'Gecikme',
    errorTitle: 'Model Yanıt Vermedi',
    timeoutTitle: 'Zaman Aşımı (Timeout)',

    // Model Selector
    modalTitle: 'Model Seçimi & Karşılaştırma',
    modalSubtitle: 'En fazla 6 modeli aynı anda yan yana karşılaştırabilirsiniz.',
    activeCount: 'Seçili Modeller',
    doneBtn: 'Seçimi Tamamla',
    categoryAll: 'Tümü',

    // Routing
    smartRouteTitle: 'Akıllı Yönlendirici',
    autoRouteOn: 'Otomatik Hedefleme Açık',
    autoRouteOff: 'Otomatik Hedefleme Kapalı',
    applyRecommended: 'Önerilen Modelleri Seç',
  },

  en: {
    // Header
    newComparison: 'New Comparison',
    modelsActive: 'Models Active',
    nvidiaLive: 'NVIDIA Live',
    noApiKey: 'API Key Missing',
    changeLanguage: 'Türkçe\'ye Geç',
    langLabel: 'TR',

    // Sidebar
    conversations: 'Comparisons',
    newChat: 'New Comparison',
    noChats: 'No comparisons yet.',
    noChatsDesc: 'Ask a question to start comparing multiple AI models.',
    deleteConfirm: 'Are you sure you want to delete this comparison?',
    today: 'Today',
    yesterday: 'Yesterday',
    older: 'Older',

    // Empty State
    heroTitle: 'One Question. Multiple Minds.',
    heroSubtitle: 'Benchmark AI model architectures, multi-step reasoning, circuit analysis, and latency side-by-side in real-time.',
    quickPresets: 'Quick Presets',
    presetCoding: 'Coding & Architecture',
    presetMath: 'Math & Formal Logic',
    presetCircuit: 'Circuit & Vision Analysis',
    presetSpeed: 'Ultra-Fast Summary',
    presetFrontier: 'Frontier Deep Synthesis',
    promptPlaceholderExample: 'Try an example prompt:',
    exampleCoding: 'Write a Python asyncio message queue worker with jittered exponential backoff and SIGINT handling.',
    exampleMath: 'Solve the equation 2^(2x) - 3 * 2^(x+2) + 32 = 0 step-by-step.',
    exampleCircuit: 'Analyze the attached diode and transistor circuit schematics: calculate output voltage Vo and branch currents.',

    // ChatInput
    inputPlaceholder: 'Ask a question or upload a photo/document (PDF, Image, Python, JSON)...',
    inputPlaceholderDocs: 'What would you like to calculate or analyze regarding the attached files/schematics?',
    systemToggle: 'System Instructions',
    systemPlaceholder: 'e.g. Show full Kirchhoff voltage/current law derivations with clear formulas.',
    modelsLabel: 'Models',
    changeModels: 'Change',
    systemBtn: 'System',
    sendBtn: 'Send to Models',
    dropHint: 'Drag and drop circuit photos, PDFs, or code files',
    uploadingHint: 'Parsing document & schematics...',
    visionRecommend: 'Nemotron Super VL 120B (Vision Model) is recommended to analyze circuit diagrams:',
    addVisionModel: '+ Add Nemotron Super VL',
    footerInfo: 'NVIDIA Build NIM Multi-Model Engine',

    // Comparison Card & Grid
    perspectives: 'Simultaneous Model Comparison',
    copy: 'Copy',
    copied: 'Copied!',
    retry: 'Retry',
    retrying: 'Retrying...',
    reasoningProcess: '🧠 Reasoning & Circuit Analysis Trace',
    hideReasoning: 'Hide Reasoning Steps',
    showReasoning: 'Show Reasoning Steps',
    finalAnswer: '⚡ Final Solution & Results',
    latency: 'Latency',
    errorTitle: 'Model Error',
    timeoutTitle: 'Request Timed Out',

    // Model Selector
    modalTitle: 'Model Selection & Comparison',
    modalSubtitle: 'Select up to 6 models to benchmark side-by-side concurrently.',
    activeCount: 'Selected Models',
    doneBtn: 'Confirm Selection',
    categoryAll: 'All',

    // Routing
    smartRouteTitle: 'Smart Intent Router',
    autoRouteOn: 'Auto-Routing Enabled',
    autoRouteOff: 'Auto-Routing Disabled',
    applyRecommended: 'Apply Recommended Models',
  }
};
