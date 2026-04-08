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
            <div class="dashboard-layout-new">
                
                <!-- ROW 1: Continue Study | Review Due Today | Start Quiz -->
                <section class="dashboard-action-row">
                    <a class="dashboard-action-card" href="{{ url_for('flashcards_session', session_id=last_session.id) if last_session else '#generate-section' }}">
                        <span class="material-symbols-outlined">play_arrow</span>
                        <div>
                            <p class="dashboard-stitch-label">Continue study</p>
                            <h2>{{ "Resume your latest session" if last_session else "Start your first session" }}</h2>
                            <small>
                                {% if last_session %}
                                    {{ last_session_remaining }}/{{ last_session.word_count }} words remaining
                                {% else %}
                                    Generate a fresh word set to begin
                                {% endif %}
                            </small>
                        </div>
                    </a>

                    <a class="dashboard-action-card dashboard-action-card-review" href="{{ url_for('review') }}">
                        <span class="material-symbols-outlined">history</span>
                        <div>
                            <p class="dashboard-stitch-label">Review due today</p>
                            <h2>{{ words_to_review_today }} words waiting</h2>
                            <small>Open your review queue and clear today's due words.</small>
                        </div>
                    </a>

                    <a class="dashboard-action-card" href="{{ url_for('quiz') }}">
                        <span class="material-symbols-outlined">timer</span>
                        <div>
                            <p class="dashboard-stitch-label">Start quiz</p>
                            <h2>Active recall session</h2>
                            <small>Test your vocabulary with focused quiz practice.</small>
                        </div>
                    </a>
                </section>

                <!-- ROW 2: Generate New Words -->
                <section class="dashboard-stitch-generate dashboard-stitch-generate-compact dashboard-grid-panel" id="generate-section">
                    <div class="generate-header-horizontal" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="flex: 1;">
                            <p class="dashboard-stitch-label">Generate new words</p>
                            <h2 style="margin: 0;">Build your next study set</h2>
                        </div>
                        <span class="dashboard-stitch-brain material-symbols-outlined" style="opacity: 0.1; font-size: 3rem;">neurology</span>
                    </div>

                    <form method="post" action="{{ url_for('generate_words') }}" class="dashboard-stitch-form generate-inline-form">
                        <div class="dashboard-stitch-form-grid generate-columns">
                            <div class="dashboard-stitch-field">
                                <label for="difficulty">Difficulty</label>
                                <select id="difficulty" name="difficulty">
                                    <option value="Beginner">Beginner</option>
                                    <option value="Intermediate" selected>Intermediate</option>
                                    <option value="Advanced">Advanced</option>
                                </select>
                            </div>
                            <div class="dashboard-stitch-field">
                                <label for="word_count">Number of words</label>
                                <select id="word_count" name="word_count">
                                    <option value="5">5 Words</option>
                                    <option value="10" selected>10 Words</option>
                                    <option value="15">15 Words</option>
                                </select>
                            </div>
                            <div class="dashboard-stitch-field">
                                <label for="custom_prompt">Custom topic</label>
                                <input type="text" id="custom_prompt" name="custom_prompt" placeholder="E.g. Business English..." value="{{ default_study_focus }}">
                            </div>
                        </div>
                        <div class="dashboard-stitch-form-footer generate-footer-inline">
                            <label class="dashboard-stitch-checkbox" for="save_as_default">
                                <input id="save_as_default" name="save_as_default" type="checkbox">
                                <span>Save as default focus</span>
                            </label>
                            <button type="submit">Generate Words</button>
                        </div>
                    </form>
                </section>

                {% set has_pending_tasks = words_to_review_today > 0 or difficult_words > 0 or (daily_goal and learned_today < daily_goal) %}

                <!-- ROW 3: Today Overview -->
                <section class="dashboard-today-overview dashboard-grid-panel today-overview-compact">
                    <div class="dashboard-today-overview-head" style="margin-bottom: 0;">
                        <div>
                            <p class="dashboard-stitch-label">Today overview</p>
                            <h3 style="margin: 0;">Focus for today</h3>
                        </div>
                        <div class="dashboard-today-overview-goal" style="margin: 0; min-width: 250px;">
                            <div class="dashboard-today-overview-goal-copy" style="margin-bottom: 0.2rem;">
                                <span>Daily goal</span>
                                <strong>{{ learned_today }} / {{ daily_goal }} words</strong>
                            </div>
                            <div class="dashboard-goal-progress" aria-label="Daily goal progress">
                                <span style="width: {{ daily_goal_percentage }}%;"></span>
                            </div>
                        </div>
                    </div>
                
                    <div class="dashboard-today-overview-stats">
                        <article class="dashboard-today-overview-stat">
                            <span>Words to review</span>
                            <strong>{{ words_to_review_today }}</strong>
                        </article>
                        <article class="dashboard-today-overview-stat">
                            <span>Difficult words</span>
                            <strong>{{ difficult_words }}</strong>
                        </article>
                        <article class="dashboard-today-overview-stat dashboard-today-overview-stat-wide" style="margin-right: auto;">
                            <span>Current streak</span>
                            <strong>{{ study_streak }} days</strong>
                        </article>
                        <div class="overview-messages-compact">
                            <!-- Messages -->
                            {% if words_to_review_today > 0 %}
                                <span><strong style="color:#fcd34d;">{{ words_to_review_today }}</strong> words to review.</span>
                            {% endif %}
                            {% if difficult_words > 0 %}
                                <span><strong style="color:#f87171;">{{ difficult_words }}</strong> difficult words.</span>
                            {% endif %}
                            {% if daily_goal and learned_today < daily_goal %}
                                <span><strong style="color:#6ee7b7;">{{ daily_goal - learned_today }}</strong> words to goal.</span>
                            {% endif %}
                            {% if not has_pending_tasks %}
                                <span style="color:#6ee7b7;">All caught up!</span>
                            {% endif %}
                        </div>
                    </div>
                </section>

                <!-- ROW 4: Recent Words | Quick Stats -->
                <section class="dashboard-row-split">
                    <section class="dashboard-stitch-recent dashboard-grid-panel">
                        <div class="dashboard-stitch-recent-head">
                            <div>
                                <p class="dashboard-stitch-label">Recent words</p>
                                <h3>Latest additions</h3>
                            </div>
                            <a href="{{ url_for('words') }}">Open My Words</a>
                        </div>
                        <div class="dashboard-stitch-recent-list compact-recent-list">
                            {% for item in recent_words[:5] %}
                                <article class="dashboard-stitch-recent-item">
                                    <div class="dashboard-stitch-recent-title">
                                        <strong>{{ item.word_entry.word }}</strong>
                                        <span>{{ item.word_entry.difficulty or "B1" }}</span>
                                    </div>
                                    <p>{{ item.word_entry.meaning|truncate(40, True, '...') }}</p>
                                </article>
                            {% else %}
                                <p class="muted">Generate a study set to start building your recent list.</p>
                            {% endfor %}
                        </div>
                    </section>

                    <section class="dashboard-stitch-stats dashboard-stitch-stats-compact dashboard-stats-grid">
                        <article class="dashboard-stitch-stat">
                            <p>Learned</p>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <strong>{{ learned_words }}</strong>
                                <span class="material-symbols-outlined">task_alt</span>
                            </div>
                        </article>
                        <article class="dashboard-stitch-stat">
                            <p>To Learn</p>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <strong>{{ unlearned_words }}</strong>
                                <span class="material-symbols-outlined">pending</span>
                            </div>
                        </article>
                        <article class="dashboard-stitch-stat dashboard-stitch-stat-danger">
                            <p>Difficult</p>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <strong>{{ difficult_words }}</strong>
                                <span class="material-symbols-outlined">bolt</span>
                            </div>
                        </article>
                        <article class="dashboard-stitch-stat dashboard-stitch-stat-primary">
                            <p>Review</p>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <strong>{{ words_to_review_today }}</strong>
                                <span class="material-symbols-outlined">history</span>
                            </div>
                        </article>
                        <article class="dashboard-stitch-stat stat-full-width">
                            <p>Streak</p>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <strong>{{ study_streak }}</strong>
                                <span class="material-symbols-outlined">local_fire_department</span>
                            </div>
                        </article>
                    </section>
                </section>

                <!-- ROW 5: Weekly Activity -->
                <section class="dashboard-stitch-chart dashboard-grid-panel weekly-compact">
                    <div class="dashboard-stitch-chart-head">
                        <div>
                            <p class="dashboard-stitch-label">Weekly activity</p>
                            <h3>Progress this week</h3>
                        </div>
                        <div class="dashboard-stitch-legend">
                            <span><i></i>Activity</span>
                        </div>
                    </div>
                    <div class="dashboard-stitch-bars dashboard-stitch-bars-compact chart-very-compact">
                        {% for item in weekly_activity %}
                            <div class="dashboard-stitch-bar-col">
                                <div class="dashboard-stitch-bar-track">
                                    <div class="dashboard-stitch-bar" style="height: {{ item.height }}px;"></div>
                                </div>
                                <span>{{ item.label }}</span>
                            </div>
                        {% endfor %}
                    </div>
                </section>

            </div>
        </section>
    </div>
</section>
{% endblock %}
'''

CSS_ADDITIONS = '''

/* --- Custom additions for new compact dashboard layout --- */
body.dashboard-page .dashboard-layout-new {
    display: grid;
    gap: 1.25rem;
    padding-bottom: 2rem;
}

body.dashboard-page .dashboard-row-split {
    display: grid;
    grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.6fr);
    gap: 1.25rem;
    align-items: stretch;
}

body.dashboard-page .dashboard-stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    align-content: start;
    height: 100%;
}

body.dashboard-page .dashboard-stats-grid .stat-full-width {
    grid-column: span 2;
}

body.dashboard-page .dashboard-stats-grid .dashboard-stitch-stat {
    padding: 1rem 1.15rem;
}

/* Compact Generate Words Section */
body.dashboard-page .generate-columns {
    grid-template-columns: 1fr 1fr 2fr;
}

body.dashboard-page .generate-inline-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

body.dashboard-page .generate-footer-inline {
    margin-top: 0;
}

/* Compact Overview Section */
body.dashboard-page .today-overview-compact .dashboard-today-overview-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 1rem;
    margin-bottom: 1rem;
}

body.dashboard-page .today-overview-compact .dashboard-today-overview-stats {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
}

body.dashboard-page .today-overview-compact .overview-messages-compact {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.7);
    border-left: 2px solid rgba(255, 255, 255, 0.1);
    padding-left: 1.25rem;
    margin-left: auto;
}

/* Compact Recent Words */
body.dashboard-page .compact-recent-list {
    margin-top: 0.5rem;
}
body.dashboard-page .compact-recent-list .dashboard-stitch-recent-item {
    padding: 0.65rem 0.85rem;
}
body.dashboard-page .compact-recent-list .dashboard-stitch-recent-item p {
    margin-top: 0.2rem;
    font-size: 0.82rem;
}

/* Weekly Chart compact */
body.dashboard-page .chart-very-compact {
    min-height: 120px;
    margin-top: 0.5rem;
}
body.dashboard-page .chart-very-compact .dashboard-stitch-bar-track {
    height: 70px;
}

@media (max-width: 900px) {
    body.dashboard-page .dashboard-row-split {
        grid-template-columns: 1fr;
    }
    body.dashboard-page .generate-columns {
        grid-template-columns: 1fr;
    }
    body.dashboard-page .today-overview-compact .overview-messages-compact {
        margin-left: 0;
        border-left: none;
        padding-left: 0;
        padding-top: 0.75rem;
        border-top: 2px solid rgba(255, 255, 255, 0.1);
        width: 100%;
    }
}
'''

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(HTML_CONTENT)

with open('static/style.css', 'a', encoding='utf-8') as f:
    f.write(CSS_ADDITIONS)

print("Updated dashboard.html and style.css")
