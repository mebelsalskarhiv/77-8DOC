/**
 * Alpine.js приложение для сравнения документов 1С 7.7 и 1С 8
 */

function app() {
    return {
        // Состояние
        startDate: '',
        endDate: '',
        docType: 'realizations',
        firmPrefix: '',
        documents: [],
        comparisonResult: null,
        loading: false,
        error: null,
        selectedDoc: null,
        showSettings: false,
        settings: {
            dbPath77: '',
            dbUser77: '',
            dbPassword77: '',
            odataUrl: '',
            odataUser: '',
            odataPassword: ''
        },

        // Инициализация
        init() {
            // Устанавливаем даты по умолчанию (текущий месяц)
            const today = new Date();
            const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

            this.startDate = this.formatDateForInput(firstDay);
            this.endDate = this.formatDateForInput(today);
            
            // Загружаем настройки из localStorage
            this.loadSettings();
        },

        // Форматирование даты для input[type="date"]
        formatDateForInput(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        },

        // Преобразование даты из YYYY-MM-DD в ДД.ММ.ГГГГ
        convertDateToRu(dateStr) {
            const [year, month, day] = dateStr.split('-');
            return `${day}.${month}.${year}`;
        },

        // Форматирование числа с разделителями
        formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            return new Intl.NumberFormat('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(num);
        },

        // Сравнение документов
        async compareDocuments() {
            this.loading = true;
            this.error = null;
            this.comparisonResult = null;

            try {
                const endpoint = `/api/v1/compare/${this.docType}`;
                const body = {
                    start_date: this.convertDateToRu(this.startDate),
                    end_date: this.convertDateToRu(this.endDate)
                };
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Ошибка при сравнении документов');
                }

                this.comparisonResult = await response.json();

                if (this.comparisonResult.documents.length === 0) {
                    this.error = 'Документы за указанный период не найдены';
                }
            } catch (err) {
                console.error('Ошибка сравнения документов:', err);
                this.error = err.message || 'Не удалось сравнить документы';
            } finally {
                this.loading = false;
            }
        },

        // Показать детали документа
        showDetails(doc) {
            this.selectedDoc = doc;
            const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
            modal.show();
        },

        // Сохранение настроек
        saveSettings() {
            localStorage.setItem('settings_77_8doc', JSON.stringify(this.settings));
            alert('Настройки сохранены в браузере');
        },

        // Загрузка настроек
        loadSettings() {
            const saved = localStorage.getItem('settings_77_8doc');
            if (saved) {
                try {
                    this.settings = JSON.parse(saved);
                } catch (e) {
                    console.error('Ошибка загрузки настроек:', e);
                }
            }
        },

        // Загрузка настроек с сервера (заглушка)
        async loadSettingsFromServer() {
            try {
                // В будущем можно добавить endpoint для получения текущих настроек
                alert('Настройки загружаются из .env файла на сервере');
            } catch (err) {
                console.error('Ошибка загрузки настроек:', err);
            }
        }
    };
}
