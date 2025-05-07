// static/js/state.js

export const scanState = {
  currentPage: 1,
  totalPages: 0,
  qrData: null,
  filename: null,
  supplementCount: 0,
  config: null,

  init(config, qrData, supplementCount) {
    this.config = config;
    this.qrData = qrData;
    this.supplementCount = supplementCount;

    const mainPages = parseInt(config.main_pages || 18);
    const supplementPages = parseInt(config.supplementPages || 4);
    this.totalPages = mainPages + supplementCount * supplementPages;

    this.filename = qrData ? qrData : generateTimestampFilename();
    this.currentPage = 1;
  },

  nextSpreadPageCount() {
    if (this.currentPage === 1 || this.currentPage === this.totalPages) return 1;
    return 2;
  },

  isLastSpread() {
    return this.currentPage >= this.totalPages;
  },

  increment() {
    this.currentPage += this.nextSpreadPageCount();
  },

  getPageInfo() {
    return {
      currentPage: this.currentPage,
      totalPages: this.totalPages,
      isLast: this.isLastSpread(),
      nextCount: this.nextSpreadPageCount(),
      filename: this.filename,
    };
  }
};

function generateTimestampFilename() {
  const now = new Date();
  const pad = (n) => n.toString().padStart(2, "0");
  return `scan_${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}
