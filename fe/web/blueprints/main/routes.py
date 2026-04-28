import json
from flask import render_template, request, redirect, url_for
from web.decorators import authorized
from web.dependencies.services import get_services
from . import main
from .forms import FilterForm, ChannelFilterForm

@main.route("/articles", methods=["GET", "POST"])
@authorized
def articles():
    services = get_services()
    filter_form = FilterForm()

    query = None
    cursor = request.args.get("cursor", None)
    cursor = None if cursor == "None" else cursor
    page = int(request.args.get("page", 1))
    history_raw = request.args.get("history", "[]")

    try:
        cursor_history = json.loads(history_raw)
        if not isinstance(cursor_history, list) or not all(isinstance(item, str) for item in cursor_history):
            cursor_history = []
    except (TypeError, json.JSONDecodeError):
        cursor_history = []

    if filter_form.validate_on_submit():
        try:
            hours = int(filter_form.hours.data)
        except Exception:
            hours = 1
        order_by_likes = filter_form.order_by_likes.data == "true"
        query = filter_form.query.data or None
    else:
        try:
            hours = int(request.args.get("hours", 1))
        except Exception:
            hours = 1
        order_by_likes = request.args.get("order_by_likes", "true") == "true"
        query = request.args.get("query", None)

    result = services.articles.read_articles(
        hours=hours,
        order_by_likes=order_by_likes,
        query=query,
        cursor=cursor,
        page=page
    )

    base_params = {
        "hours": hours,
        "order_by_likes": str(order_by_likes).lower(),
        "query": query,
    }

    is_search = query is not None and query.strip() != ""
    prev_page_cursor = None

    if is_search:
        prev_page_url = url_for("main.articles", page=page - 1, **base_params) if page > 1 else None
        next_page_url = url_for("main.articles", page=result.next_page,
                                **base_params) if result.has_more and result.next_page else None
        has_previous = page > 1
    else:
        has_previous = cursor is not None
        prev_page_cursor = cursor_history[-1] if cursor_history else None
        prev_history = cursor_history[:-1] if cursor_history else []
        next_history = cursor_history + ([cursor] if cursor is not None else [])

        prev_page_url = None
        if has_previous:
            prev_page_url = url_for(
                "main.articles",
                cursor=prev_page_cursor,
                history=json.dumps(prev_history),
                **base_params,
            )

        next_page_url = None
        if result.has_more and result.next_cursor:
            next_page_url = url_for(
                "main.articles",
                cursor=result.next_cursor,
                history=json.dumps(next_history),
                **base_params,
            )

    return render_template(
        "main/articles.html",
        articles=result.articles if result.articles else [],
        filter_form=filter_form,
        current_hours = hours,
        has_more = result.has_more,
        next_cursor = result.next_cursor,
        current_cursor = cursor,
        has_previous = has_previous,
        prev_cursor = prev_page_cursor,
        prev_page_url = prev_page_url,
        next_page_url = next_page_url,
        current_order_by_likes=str(order_by_likes).lower(),
        current_query=query
    )


@main.route("/article/<uuid>", methods = ["GET", "POST"])
def article(uuid):
    services = get_services()
    return render_template("main/article.html", article=services.articles.read_article(uuid))


@main.route("/like_article/<uuid>", methods=["POST"])
@authorized
def like_article(uuid):
    services = get_services()
    liked = services.articles.like_article(uuid)
    return {"liked": liked}

@main.route("/channels", methods=["GET", "POST"])
@authorized
def channels():
    services = get_services()
    all_channels = services.channels.get_all_channels()
    form = ChannelFilterForm()

    if form.validate_on_submit():
        disabled_uuids = request.form.getlist("disabled")
        disabled_channels = [channel for channel in all_channels if channel.uuid in disabled_uuids]
        services.channels.set_disabled_channels(disabled_channels)

        return redirect(url_for('main.channels'))

    return render_template("main/channels.html", channels=all_channels, form=form)
