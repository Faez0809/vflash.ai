import os

HTML_CONTENT = '''{% extends "base.html" %}

{% block title %}Dashboard | vflash.ai{% endblock %}

{% block content %}
<section class="dashboard-page-wrap">
    <header class="dashboard-topbar">
        <div class="dashboard-topbar-brand">
            <a href="{{ url_for('dashboard') }}">vflash.ai</a>
        </div>
        <form class="dashboard-topbar-search" action="{{ url_for('search_word') }}" method="get">
            <span class="material-symbols-outlined">search</span>
            <input type="search" name="q" placeholder="Search any word">
        </form>
        <div class="dashboard-topbar-actions">
            <a class="dashboard-topbar-cta" href="#generate-section">New Session</a>
            <a class="dashboard-avatar" href="{{ url_for('profile') }}" aria-label="Profile">
                {{ display_name[:1]|upper }}
            </a>
        </div>
    </header>

    <div class="dashboard-layout">
        <aside class="dashboard-sidebar">
            <div class="dashboard-sidebar-profile">
                <div class="dashboard-sidebar-badge">
                    <span class="material-symbols-outlined">book_2</span>
                </div>
                <div>
                    <strong>{{ display_name }}</strong>
                    <span title="{{ current_user.default_study_focus or 'General vocabulary practice' }}">{{ (current_user.default_study_focus or "General vocabulary practice")|truncate(28, True, '...') }}</span>
                </div>
            </div>

            <nav class="dashboard-sidebar-nav">
                <a class="is-active" href="{{ url_for('dashboard') }}">
                    <span class="material-symbols-outlined">dashboard</span>
                    <span>Dashboard</span>
                </a>
                <a href="{{ url_for('words') }}">
                    <span class="material-symbols-outlined">style</span>
                    <span>Word Lists</span>
                </a>
                <a href="{{ url_for('flashcards') }}">
                    <span class="material-symbols-outlined">amp_stories</span>
                    <span>Flashcards</span>
                </a>
                <a href="{{ url_for('quiz') }}">
                    <span class="material-symbols-outlined">quiz</span>
                    <span>Quizzes</span>
                </a>
                <a href="{{ url_for('review') }}">
                    <span class="material-symbols-outlined">rule</span>
                    <span>Review</span>
                </a>
                <a href="{{ url_for('profile') }}">
                    <span class="material-symbols-outlined">person</span>
                    <span>Profile</span>
                </a>
                <a href="{{ url_for('logout') }}">
                    <span class="material-symbols-outlined">logout</span>
                    <span>Sign Out</span>
                </a>
            </nav>
        </aside>

        <section class="dashboard-main">
            <div class="dashboard-layout-extreme-compact">
                
                <!-- ROW 1: Continue Study | Review Due Today | Start Quiz -->
                <section class="dashboard-action-row">
                    <a class="dashboard-action-card" href="{{ url_for('flashcards_session', session_id=last_session.id) if last_session else '#generate-section' }}">
                        <span class="material-symbols-outlined">play_arrow</span>
                        <div>
                            <p class="dashboard-stitch-label">Continue study</p>
                            <h2>{{ "Resume latest session" if last_session else "Start first session" }}</h2>
                            <small>
                                {% if last_session %}
                                    {{ last_session_remaining }}/{{ last_session.word_count }} words left
                                {% else %}
                                    Create a fresh word set
                                {% endif %}
                            </small>
                        </div>
                    </a>

                    <a class="dashboard-action-card dashboard-action-card-review" href="{{ url_for('review') }}">
                        <span class="material-symbols-outlined">history</span>
                        <div>
                            <p class="dashboard-stitch-label">Review due today</p>
                            <h2>{{ words_to_review_today }} words</h2>
                            <small>Clear your due queue.</small>
                        </div>
                    </a>

                    <a class="dashboard-action-card" href="{{ url_for('quiz') }}">
                        <span class="material-symbols-outlined">timer</span>
                        <div>
                            <p class="dashboard-stitch-label">Start quiz</p>
                            <h2>Active recall</h2>
                            <small>Focused practice.</small>
                        </div>
                    </a>
                </section>

                <!-- ROW 2: Generate New Words (FULL WIDTH) -->
                <section class="dashboard-stitch-generate dashboard-grid-panel generate-panel-ultra-compact" id="generate-section">
                    <div class="generate-header-horizontal">
                        <div>
                            <h2 style="margin: 0; font-size: 1.2rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span class="material-symbols-outlined" style="font-size: 1.4rem; color: var(--accent);">neurology</span>
                                Generate build your next study set
                            </h2>
                        </div>
                    </div>

                    <form method="post" action="{{ url_for('generate_words') }}" class="dashboard-stitch-form generate-inline-form-row">
                        <div class="dashboard-stitch-form-grid generate-columns-flex">
                            <div class="dashboard-stitch-field field-small">
                                <select id="difficulty" name="difficulty" aria-label="Difficulty">
                                    <option value="Beginner">Beginner</option>
                                    <option value="Intermediate" selected>Intermediate</option>
                                    <option value="Advanced">Advanced</option>
                                </select>
                            </div>
                            <div class="dashboard-stitch-field field-small">
                                <select id="word_count" name="word_count" aria-label="Number of words">
                                    <option value="5">5 Words</option>
                                    <option value="10" selected>10 Words</option>
                                    <option value="15">15 Words</option>
                                </select>
                            </div>
                            <div class="dashboard-stitch-field field-expand">
                                <input type="text" id="custom_prompt" name="custom_prompt" placeholder="Custom topic: Business English, IELTS..." value="{{ default_study_focus }}" aria-label="Custom topic">
                            </div>
                            <div class="dashboard-stitch-form-footer generate-footer-flex">
                                <button type="submit" class="btn-generate-compact">Generate</button>
                            </div>
                        </div>
                    </form>
                </section>

                {% set has_pending_tasks = words_to_review_today > 0 or difficult_words > 0 or (daily_goal and learned_today < daily_goal) %}

                <!-- ROW 3 & 4: Two Column Layout -->
                <section class="dashboard-two-col-engine">
                    <!-- LEFT COLUMN -->
                    <div class="dashboard-col-left">
                        <!-- Today Overview -->
                        <section class="dashboard-today-overview dashboard-grid-panel today-overview-ultra">
                            <div class="dashboard-today-overview-head" style="margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.06);">
                                <div>
                                    <h3 style="margin: 0; font-size: 1.15rem;">Today overview</h3>
                                </div>
                                <div class="dashboard-today-overview-goal" style="margin: 0; min-width: 200px;">
                                    <div class="dashboard-today-overview-goal-copy" style="margin-bottom: 0.15rem; font-size: 0.85rem;">
                                        <span>Daily goal</span>
                                        <strong>{{ learned_today }} / {{ daily_goal }} words</strong>
                                    </div>
                                    <div class="dashboard-goal-progress" aria-label="Daily goal progress" style="height: 6px;">
                                        <span style="width: {{ daily_goal_percentage }}%;"></span>
                                    </div>
                                </div>
                            </div>
                        
                            <div class="dynamic-motivational-message">
                                {% set completion_rate = (learned_today / daily_goal * 100) if daily_goal > 0 else 0 %}
                                {% if study_streak >= 7 %}
                                    <p>🔥 <strong>You're on fire!</strong> {{ study_streak }} day streak. Keep the momentum going!</p>
                                {% elif completion_rate >= 100 %}
                                    <p>⭐ <strong>Goal crushed!</strong> You're making excellent progress today.</p>
                                {% elif words_to_review_today > 20 %}
                                    <p>⏳ A busy review day ahead. Knock out those {{ words_to_review_today }} words!</p>
                                {% elif completion_rate > 50 %}
                                    <p>📈 More than halfway to your daily goal. Keep it up!</p>
                                {% elif words_to_review_today == 0 and unlearned_words == 0 and completion_rate == 0 %}
                                    <p>🌱 Start a new session and build your vocabulary today.</p>
                                {% elif not has_pending_tasks %}
                                    <p>🏆 <strong>Incredible work!</strong> You're all caught up for the day.</p>
                                {% else %}
                                    <p>💡 Every word counts. Keep pushing towards your daily goal!</p>
                                {% endif %}
                            </div>
                        </section>

                        <!-- Recent Words -->
                        <section class="dashboard-stitch-recent dashboard-grid-panel recent-ultra-compact">
                            <div class="dashboard-stitch-recent-head" style="margin-bottom: 0.5rem;">
                                <div>
                                    <h3 style="margin: 0; font-size: 1.15rem;">Recent words</h3>
                                </div>
                                <a href="{{ url_for('words') }}" style="font-size: 0.8rem;">View All</a>
                            </div>
                            <div class="dashboard-stitch-recent-list compact-4-items">
                                {% for item in recent_words[:5] %}
                                    <article class="dashboard-stitch-recent-item" style="padding: 0.4rem 0.6rem; border-radius: 8px;">
                                        <div class="dashboard-stitch-recent-title">
                                            <strong style="font-size: 0.95rem;">{{ item.word_entry.word }}</strong>
                                            <span style="font-size: 0.7rem; padding: 0.1rem 0.3rem;">{{ item.word_entry.difficulty or "B1" }}</span>
                                        </div>
                                        <p style="margin: 0.1rem 0 0; font-size: 0.8rem; line-height: 1.3;">{{ item.word_entry.meaning|truncate(45, True, '...') }}</p>
                                    </article>
                                {% else %}
                                    <p class="muted" style="font-size: 0.85rem;">No recent words yet.</p>
                                {% endfor %}
                            </div>
                        </section>
                    </div>

                    <!-- RIGHT COLUMN -->
                    <div class="dashboard-col-right">
                        <!-- Quick Stats -->
                        <section class="dashboard-stitch-stats dashboard-stitch-stats-compact stats-2x3-grid">
                            <article class="dashboard-stitch-stat small-stat-card">
                                <p>Learned</p>
                                <div>
                                    <strong>{{ learned_words }}</strong>
                                </div>
                            </article>
                            <article class="dashboard-stitch-stat small-stat-card">
                                <p>To Learn</p>
                                <div>
                                    <strong>{{ unlearned_words }}</strong>
                                </div>
                            </article>
                            <article class="dashboard-stitch-stat dashboard-stitch-stat-danger small-stat-card">
                                <p>Difficult</p>
                                <div>
                                    <strong>{{ difficult_words }}</strong>
                                </div>
                            </article>
                            <article class="dashboard-stitch-stat dashboard-stitch-stat-primary small-stat-card">
                                <p>Review</p>
                                <div>
                                    <strong>{{ words_to_review_today }}</strong>
                                </div>
                            </article>
                            <article class="dashboard-stitch-stat stat-span-2 small-stat-card">
                                <p>Streak</p>
                                <div style="display: flex; align-items: center; gap: 0.4rem;">
                                    <strong>{{ study_streak }}</strong>
                                    <span class="material-symbols-outlined" style="font-size: 1.2rem; color: #f97316;">local_fire_department</span>
                                </div>
                            </article>
                        </section>

                        <!-- Weekly Activity Chart (UNDER Quick Stats) -->
                        <section class="dashboard-stitch-chart dashboard-grid-panel weekly-mini">
                            <div class="dashboard-stitch-chart-head" style="margin-bottom: 0.5rem;">
                                <div>
                                    <h3 style="margin: 0; font-size: 1.05rem;">Weekly activity</h3>
                                </div>
                            </div>
                            <div class="dashboard-stitch-bars mini-chart-bars">
                                {% for item in weekly_activity %}
                                    <div class="dashboard-stitch-bar-col">
                                        <div class="dashboard-stitch-bar-track">
                                            <!-- Scaled down height inline for mini chart -->
                                            <div class="dashboard-stitch-bar" style="height: {{ item.height * 0.6 }}px;"></div>
                                        </div>
                                        <span style="font-size: 0.65rem;">{{ item.label[:1] }}</span>
                                    </div>
                                {% endfor %}
                            </div>
                        </section>
                    </div>
                </section>
            </div>
        </section>
    </div>
</section>
{% endblock %}
'''

CSS_ADDITIONS = '''
/* --- ULtra Compact 2-Column Layout Overrides --- */

body.dashboard-page .dashboard-layout-extreme-compact {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    padding-bottom: 1.5rem;
}

body.dashboard-page .dashboard-action-row {
    gap: 0.8rem;
}

body.dashboard-page .dashboard-action-card {
    padding: 1rem;
}
body.dashboard-page .dashboard-action-card h2 {
    font-size: 1.1rem;
    margin-bottom: 0.2rem;
}
body.dashboard-page .dashboard-action-card p.dashboard-stitch-label {
    margin-bottom: 0.2rem;
}

/* Generate full width but thin */
body.dashboard-page .generate-panel-ultra-compact {
    padding: 0.8rem 1rem;
}

body.dashboard-page .generate-columns-flex {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-top: 0.5rem;
}

body.dashboard-page .generate-columns-flex .field-small {
    flex: 0 0 140px;
}
body.dashboard-page .generate-columns-flex .field-expand {
    flex: 1;
}

body.dashboard-page .generate-columns-flex select,
body.dashboard-page .generate-columns-flex input {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
}

body.dashboard-page .btn-generate-compact {
    padding: 0.5rem 1.25rem;
    font-size: 0.9rem;
    min-width: 0;
}

/* 2-Column Dashboard Engine */
body.dashboard-page .dashboard-two-col-engine {
    display: grid;
    grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
    gap: 0.8rem;
    align-items: start;
}

body.dashboard-page .dashboard-col-left {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

body.dashboard-page .dashboard-col-right {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

/* Motivational Message */
body.dashboard-page .dynamic-motivational-message {
    padding: 0.75rem 0;
    margin: 0;
}
body.dashboard-page .dynamic-motivational-message p {
    margin: 0;
    font-size: 0.95rem;
    color: rgba(255,255,255,0.85);
    line-height: 1.4;
}

body.dashboard-page .today-overview-ultra {
    padding: 1rem;
}

body.dashboard-page .recent-ultra-compact {
    padding: 1rem;
}
body.dashboard-page .compact-4-items {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

/* Quick Stats 2x3 Grid */
body.dashboard-page .stats-2x3-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
}

body.dashboard-page .small-stat-card {
    padding: 0.75rem 0.85rem;
}
body.dashboard-page .small-stat-card p {
    margin-bottom: 0.25rem;
    font-size: 0.75rem;
    color: rgba(255,255,255,0.6);
}
body.dashboard-page .small-stat-card strong {
    font-size: 1.25rem;
    line-height: 1;
}

body.dashboard-page .stat-span-2 {
    grid-column: span 2;
}

/* Mini Chart under stats */
body.dashboard-page .weekly-mini {
    padding: 0.85rem 1rem;
}
body.dashboard-page .mini-chart-bars {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    height: 70px;
    margin-top: 0.25rem;
}
body.dashboard-page .mini-chart-bars .dashboard-stitch-bar-track {
    width: 20px;
    height: 55px;
    background: rgba(255,255,255,0.04);
    border-radius: 4px;
    display: flex;
    align-items: flex-end;
}
body.dashboard-page .mini-chart-bars .dashboard-stitch-bar {
    width: 100%;
    border-radius: 4px;
}
body.dashboard-page .mini-chart-bars .dashboard-stitch-bar-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
}

@media (max-width: 900px) {
    body.dashboard-page .dashboard-two-col-engine {
        grid-template-columns: 1fr;
    }
    body.dashboard-page .generate-columns-flex {
        flex-direction: column;
        align-items: stretch;
    }
    body.dashboard-page .generate-columns-flex .field-small {
        flex: auto;
    }
}
'''

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(HTML_CONTENT)

# Avoid adding CSS_ADDITIONS repeatedly if run twice. Note we trust this runs once cleanly.
with open('static/style.css', 'a', encoding='utf-8') as f:
    f.write(CSS_ADDITIONS)

print("Updated dashboard.html and style.css for exact compact layout")
