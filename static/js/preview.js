let isBookletView = true;
let currentPages = [];

/**
 * Adds a page preview and updates the display
 */
export function addPagePreview(src, pageNumber) {
  const img = new Image();
  img.src = typeof src === 'string' ? src : URL.createObjectURL(src);
  img.alt = `Page ${pageNumber}`;
  img.dataset.pageNum = pageNumber;
  img.className = 'booklet-page';
  img.loading = 'lazy';

  currentPages.push({ img, pageNumber });
  renderCurrentView();
}

/**
 * Renders all pages in the current view mode
 */
function renderCurrentView() {
  const container = document.getElementById("previewContainer");
  if (!container) return;

  container.innerHTML = '';

  currentPages.sort((a, b) => a.pageNumber - b.pageNumber);

  if (isBookletView) {
    renderBookletView(container);
  } else {
    renderListView(container);
  }
}

/**
 * Renders pages in booklet-style spreads with even-left and odd-right
 */
function renderBookletView(container) {
  const spreads = [];
  let i = 0;

  while (i < currentPages.length) {
    const current = currentPages[i];

    if (shouldDisplaySingle(current.pageNumber)) {
      spreads.push([current]);
      i++;
    } else {
      const next = currentPages[i + 1];
      if (next && !shouldDisplaySingle(next.pageNumber)) {
        // ✅ Ensure even comes before odd (left | right)
        const pair = [current, next].sort((a, b) => a.pageNumber - b.pageNumber);
        spreads.push(pair);
        i += 2;
      } else {
        spreads.push([current]);
        i++;
      }
    }
  }

  spreads.forEach(spread => {
    const spreadContainer = document.createElement('div');
    spreadContainer.className = 'spread-container';

    if (spread.length === 1) {
      spreadContainer.appendChild(createPageElement(spread[0]));
    } else {
      const spreadDiv = document.createElement('div');
      spreadDiv.className = 'booklet-spread';

      spreadDiv.appendChild(createPageElement(spread[0])); // left
      spreadDiv.appendChild(createPageElement(spread[1])); // right

      spreadContainer.appendChild(spreadDiv);
    }

    container.appendChild(spreadContainer);
  });
}

/**
 * Renders pages vertically in list view
 */
function renderListView(container) {
  currentPages.forEach(page => {
    const pageContainer = document.createElement('div');
    pageContainer.className = 'spread-container single-page';
    pageContainer.appendChild(createPageElement(page));
    container.appendChild(pageContainer);
  });
}

/**
 * Creates a page element with left/right styling
 */
function createPageElement(page) {
  const wrapper = document.createElement('div');
  wrapper.className = 'page-wrapper ' + (page.pageNumber % 2 === 0 ? 'left-page' : 'right-page');

  const img = page.img.cloneNode();
  wrapper.appendChild(img);

  const label = document.createElement('div');
  label.className = 'page-label';
  label.textContent = `Page ${page.pageNumber}`;
  wrapper.appendChild(label);

  return wrapper;
}

/**
 * Determines if a page should be displayed alone
 */
function shouldDisplaySingle(pageNum) {
  const lastPage = Math.max(...currentPages.map(p => p.pageNumber));
  if (pageNum === 1 || pageNum === lastPage) return true;

  if (pageNum > 32) {
    const offset = pageNum - 33;
    const posInSupplement = offset % 4;
    return posInSupplement === 0 || posInSupplement === 3;
  }

  return false;
}

/**
 * Clears all previews
 */
export function clearPreviews() {
  currentPages = [];
  const container = document.getElementById("previewContainer");
  if (container) {
    container.innerHTML = '';
  }
}

/**
 * Sets up view toggle
 */
function initViewToggle() {
  const toggleBtn = document.getElementById('toggleViewBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      isBookletView = !isBookletView;
      toggleBtn.textContent = isBookletView ? 'List View' : 'Booklet View';
      renderCurrentView();
    });
  }
}

document.addEventListener('DOMContentLoaded', initViewToggle);
