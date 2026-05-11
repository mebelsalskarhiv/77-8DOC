/**
 * Alpine.js приложение для работы с документами 1С
 */

function app() {
    return {
        // Состояние
        startDate: '',
        endDate: '',
        docType: 'realizations',
        documents: [],
        loading: false,
        error: null,
        selectedDoc: null,

        // Инициализация
        init() {
            // Устанавливаем даты по умолчанию (текущий месяц)
            const today = new Date();
            const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

            this.startDate = this.formatDateForInput(firstDay);
            this.endDate = this.formatDateForInput(today);
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

        // Вычисление общей суммы
        get totalSum() {
            return this.documents.reduce((sum, doc) => sum + (doc.sum || 0), 0);
        },

        // Форматирование числа с разделителями
        formatNumber(num) {
            if (num === null || num === undefined) return '0.00';
            return new Intl.NumberFormat('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(num);
        },

        // Загрузка документов
        async loadDocuments() {
            this.loading = true;
            this.error = null;
            this.documents = [];

            try {
                const endpoint = `/api/v1/${this.docType}`;
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        start_date: this.convertDateToRu(this.startDate),
                        end_date: this.convertDateToRu(this.endDate)
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Ошибка при загрузке документов');
                }

                this.documents = await response.json();

                if (this.documents.length === 0) {
                    this.error = 'Документы за указанный период не найдены';
                }
            } catch (err) {
                console.error('Ошибка загрузки документов:', err);
                this.error = err.message || 'Не удалось загрузить документы';
            } finally {
                this.loading = false;
            }
        },

        // Показать детали документа
        showDetails(doc) {
            this.selectedDoc = doc;
            const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
            modal.show();
        }
    };
}
