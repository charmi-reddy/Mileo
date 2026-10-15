const state = {
  deck: [],
  currentIndex: 0,
  selectedMinutes: null,
  routeName: '',
  commuteMinutes: 0,
  sessionStarted: false,
  answerVisible: false,
  saveLocked: false,
  currentSession: null,
  reviewQueue: [],
  sessionCards: [],
  reviewPass: false,
  understoodCount: 0,
};

const elements = {
  setupView: document.getElementById('setup-view'),
  studyView: document.getElementById('study-view'),
  confirmView: document.getElementById('confirm-view'),
  dashboardView: document.getElementById('dashboard-view'),
  routeName: document.getElementById('route-name'),
  commuteMinutes: document.getElementById('commute-minutes'),
  sessionLength: document.getElementById('session-length'),
  sessionButtons: Array.from(document.querySelectorAll('.session-btn')),
  startSessionBtn: document.getElementById('start-session-btn'),
  setUpError: document.getElementById('setup-error'),
  studyProgress: document.getElementById('study-progress'),
  studyStatus: document.getElementById('study-status'),
  questionText: document.getElementById('question-text'),
  answerBlock: document.getElementById('answer-block'),
  answerText: document.getElementById('answer-text'),
  explanationText: document.getElementById('explanation-text'),
  showAnswerBtn: document.getElementById('show-answer-btn'),
  responseActions: document.getElementById('response-actions'),
  understoodBtn: document.getElementById('understood-btn'),
  reviewBtn: document.getElementById('review-btn'),
  endSessionBtn: document.getElementById('end-session-btn'),
  confirmError: document.getElementById('confirm-error'),
  actualMinutes: document.getElementById('actual-minutes'),
  saveSessionBtn: document.getElementById('save-session-btn'),
  toast: document.getElementById('toast'),
  hoursReclaimed: document.getElementById('hours-reclaimed'),
  chartBars: document.getElementById('chart-bars'),
  recentSessionsList: document.getElementById('recent-sessions-list'),
};

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.remove('hidden');
  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => {
    elements.toast.classList.add('hidden');
  }, 2000);
}

function hideAllViews() {
  [
    elements.setupView,
    elements.studyView,
    elements.confirmView,
    elements.dashboardView,
  ].forEach((view) => view.classList.add('hidden'));
}

function showView(view) {
  hideAllViews();
  view.classList.remove('hidden');
}

async function loadSettings() {
  const response = await fetch('/api/settings');
  if (!response.ok) return;
  const settings = await response.json();
  elements.routeName.value = settings.route_name || '';
  elements.commuteMinutes.value = settings.commute_minutes || 0;
  state.routeName = settings.route_name || '';
  state.commuteMinutes = Number(settings.commute_minutes || 0);
}

async function loadDeck() {
  const response = await fetch('/api/deck');
  if (!response.ok) return;
  const data = await response.json();
  state.deck = data.deck || [];
}

async function loadSummary() {
  const response = await fetch('/api/summary');
  if (!response.ok) return;
  const summary = await response.json();
  const hours = Number(summary.hours_reclaimed || 0);
  elements.hoursReclaimed.textContent = `${hours.toFixed(1)} hrs reclaimed`;

  const maxMinutes = Math.max(...(summary.daily || []).map((day) => Number(day.minutes || 0)), 1);
  elements.chartBars.innerHTML = '';

  (summary.daily || []).forEach((day) => {
    const column = document.createElement('div');
    column.className = 'bar-column';

    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.height = `${Math.max((Number(day.minutes || 0) / maxMinutes) * 100, 8)}%`;
    bar.title = `${day.day}: ${day.minutes} minutes`;

    const label = document.createElement('div');
    label.className = 'day-label';
    label.textContent = day.day;

    column.appendChild(bar);
    column.appendChild(label);
    elements.chartBars.appendChild(column);
  });

  elements.recentSessionsList.innerHTML = '';
  (summary.recent_sessions || []).forEach((session) => {
    const item = document.createElement('li');
    item.className = 'session-item';

    const meta = document.createElement('div');
    meta.innerHTML = `<strong>${session.route_name}</strong><br><span>${session.created_at}</span>`;

    const minutes = document.createElement('div');
    minutes.textContent = `${session.actual_minutes} min`;

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'secondary-btn';
    deleteBtn.type = 'button';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', async () => {
      const confirmed = window.confirm('Delete this session? Your weekly total will update.');
      if (!confirmed) return;
      const response = await fetch(`/api/sessions/${session.id}`, { method: 'DELETE' });
      if (response.ok) {
        showToast('Session removed');
        await loadSummary();
      }
    });

    item.appendChild(meta);
    item.appendChild(minutes);
    item.appendChild(deleteBtn);
    elements.recentSessionsList.appendChild(item);
  });

  if (!summary.recent_sessions || summary.recent_sessions.length === 0) {
    const empty = document.createElement('li');
    empty.className = 'session-item';
    empty.textContent = 'No recent sessions';
    elements.recentSessionsList.appendChild(empty);
  }
}

function updateSetupValidation() {
  const routeName = elements.routeName.value.trim();
  const commuteMinutes = Number(elements.commuteMinutes.value || 0);
  state.routeName = routeName;
  state.commuteMinutes = commuteMinutes;

  const customMinutes = Number(elements.sessionLength.value || 0);
  if (customMinutes > 0) {
    state.selectedMinutes = customMinutes;
    elements.sessionButtons.forEach((button) => button.classList.remove('selected'));
    return;
  }

  if (regionSelectedMinutes()) {
    elements.sessionButtons.forEach((button) => {
      button.classList.toggle('selected', Number(button.dataset.minutes) === state.selectedMinutes);
    });
  }
}

function regionSelectedMinutes() {
  return Number.isFinite(state.selectedMinutes) && state.selectedMinutes > 0;
}

function setError(element, message) {
  element.textContent = message;
  element.classList.toggle('hidden', !message);
}

function validateSetup() {
  const routeName = elements.routeName.value.trim();
  const commuteMinutes = Number(elements.commuteMinutes.value || 0);
  const customMinutes = Number(elements.sessionLength.value || 0);

  if (!routeName) {
    setError(elements.setUpError, 'Route name is required.');
    return false;
  }

  if (!Number.isFinite(commuteMinutes) || commuteMinutes <= 0) {
    setError(elements.setUpError, 'Commute time must be a valid positive number.');
    return false;
  }

  if (customMinutes > 0) {
    state.selectedMinutes = customMinutes;
  }

  if (!regionSelectedMinutes()) {
    setError(elements.setUpError, 'Choose a session length to continue.');
    return false;
  }

  if (commuteMinutes < state.selectedMinutes) {
    setError(elements.setUpError, 'Commute time must be at least the selected session length.');
    return false;
  }

  setError(elements.setUpError, '');
  state.routeName = routeName;
  state.commuteMinutes = commuteMinutes;
  return true;
}

async function saveSettings() {
  const payload = {
    route_name: elements.routeName.value.trim(),
    commute_minutes: Number(elements.commuteMinutes.value || 0),
    timezone: 'Asia/Kolkata',
  };

  await fetch('/api/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

function renderCard() {
  if (!state.sessionCards.length) return;
  const card = state.sessionCards[state.currentIndex];
  if (!card) return;

  elements.questionText.textContent = card.question;
  elements.answerText.textContent = card.answer;
  elements.explanationText.textContent = card.explanation || '';
  elements.answerBlock.classList.add('hidden');
  elements.responseActions.classList.add('hidden');
  elements.showAnswerBtn.classList.remove('hidden');
  elements.answerVisible = false;

  const totalCards = state.sessionCards.length;
  const currentPosition = state.currentIndex + 1;
  if (state.reviewPass) {
    elements.studyProgress.textContent = `Review ${currentPosition} of ${totalCards}`;
    elements.studyStatus.textContent = `Review queue: ${state.reviewQueue.length} • Understood: ${state.understoodCount}`;
  } else {
    elements.studyProgress.textContent = `Card ${currentPosition} of ${state.deck.length}`;
    elements.studyStatus.textContent = `Initial pass • Understood: ${state.understoodCount} • Review: ${state.reviewQueue.length}`;
  }
}

function resetSessionState() {
  state.sessionCards = [...state.deck];
  state.reviewQueue = [];
  state.reviewPass = false;
  state.currentIndex = 0;
  state.understoodCount = 0;
}

function startSession() {
  if (!validateSetup()) return;

  state.sessionStarted = true;
  resetSessionState();
  state.answerVisible = false;
  state.currentSession = {
    route_name: state.routeName,
    planned_minutes: state.selectedMinutes,
  };

  renderCard();
  showView(elements.studyView);
  saveSettings();
}

function finishOrReview() {
  state.sessionCards.splice(state.currentIndex, 1);

  if (state.sessionCards.length === 0) {
    if (state.reviewQueue.length > 0 && !state.reviewPass) {
      state.reviewPass = true;
      state.sessionCards = [...state.reviewQueue];
      state.reviewQueue = [];
      state.currentIndex = 0;
      renderCard();
      return;
    }
    openConfirmScreen();
    return;
  }

  if (state.currentIndex >= state.sessionCards.length) {
    state.currentIndex = 0;
  }

  renderCard();
}

function markCurrentCard(reviewAgain) {
  const card = state.sessionCards[state.currentIndex];
  if (!card) {
    openConfirmScreen();
    return;
  }

  if (reviewAgain) {
    const alreadyQueued = state.reviewQueue.some((item) => item.id === card.id);
    if (!alreadyQueued) {
      state.reviewQueue.push(card);
    }
    if (state.reviewPass && state.reviewQueue.length > 0 && state.sessionCards.length === 1) {
      state.reviewQueue = [];
      openConfirmScreen();
      return;
    }
  } else {
    state.understoodCount += 1;
  }

  finishOrReview();
}

function openConfirmScreen() {
  elements.actualMinutes.value = String(state.currentSession?.planned_minutes || 0);
  setError(elements.confirmError, '');
  showView(elements.confirmView);
}

async function saveSession() {
  if (state.saveLocked) return;

  const actualMinutes = Number(elements.actualMinutes.value || 0);
  const plannedMinutes = state.currentSession?.planned_minutes || 0;

  if (!Number.isFinite(actualMinutes) || actualMinutes <= 0) {
    setError(elements.confirmError, 'Study minutes must be greater than zero.');
    return;
  }

  if (actualMinutes > plannedMinutes) {
    setError(elements.confirmError, 'Study minutes cannot exceed the planned session length.');
    return;
  }

  state.saveLocked = true;
  elements.saveSessionBtn.disabled = true;

  const response = await fetch('/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      route_name: state.currentSession?.route_name || state.routeName,
      planned_minutes: plannedMinutes,
      actual_minutes: actualMinutes,
      timezone: 'Asia/Kolkata',
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    state.saveLocked = false;
    elements.saveSessionBtn.disabled = false;
    setError(elements.confirmError, data.error || 'Unable to save session.');
    return;
  }

  setError(elements.confirmError, '');
  showToast('Session saved');
  await loadSummary();
  showView(elements.dashboardView);
  state.saveLocked = false;
  elements.saveSessionBtn.disabled = false;
}

function bindEvents() {
  elements.sessionButtons.forEach((button) => {
    button.addEventListener('click', () => {
      elements.sessionButtons.forEach((btn) => btn.classList.remove('selected'));
      button.classList.add('selected');
      elements.sessionLength.value = '';
      state.selectedMinutes = Number(button.dataset.minutes);
      setError(elements.setUpError, '');
    });
  });

  elements.routeName.addEventListener('input', updateSetupValidation);
  elements.commuteMinutes.addEventListener('input', updateSetupValidation);
  elements.sessionLength.addEventListener('input', () => {
    const customMinutes = Number(elements.sessionLength.value || 0);
    elements.sessionButtons.forEach((button) => button.classList.remove('selected'));
    state.selectedMinutes = customMinutes > 0 ? customMinutes : null;
    setError(elements.setUpError, '');
  });

  elements.startSessionBtn.addEventListener('click', () => {
    if (validateSetup()) {
      startSession();
    }
  });

  [elements.routeName, elements.commuteMinutes, elements.sessionLength].forEach((field) => {
    field.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        if (validateSetup()) {
          startSession();
        }
      }
    });
  });

  elements.showAnswerBtn.addEventListener('click', () => {
  elements.answerBlock.classList.remove('hidden');
  elements.explanationText.classList.remove('hidden');
  elements.responseActions.classList.remove('hidden');
  elements.showAnswerBtn.classList.add('hidden');
  elements.answerVisible = true;
  });

  elements.understoodBtn.addEventListener('click', () => {
    markCurrentCard(false);
  });

  elements.reviewBtn.addEventListener('click', () => {
    markCurrentCard(true);
  });

  elements.endSessionBtn.addEventListener('click', () => {
    openConfirmScreen();
  });

  elements.saveSessionBtn.addEventListener('click', saveSession);
}

async function init() {
  await loadSettings();
  await loadDeck();
  await loadSummary();
  bindEvents();
  showView(elements.setupView);
  elements.setupView.classList.add('active');
}

init();
