from web.decorators import authorized
from web.dependencies.services import get_services
from .forms import CredentialsForm, GenerateInviteForm
from web.api_client.models import UpdateCredentialsDTO, TokenResponse
from flask import redirect, url_for, render_template, request, flash
from web.utils.auth import set_auth_cookie, delete_auth_cookie
from . import user

@user.route("/profile", methods=["GET", "POST"])
@authorized
def profile():
    services = get_services()
    form = CredentialsForm()
    invite_form = GenerateInviteForm()
    invite_code = None

    if invite_form.validate_on_submit():
        try:
            invite_code = services.consumers.generate_code()
            flash("Pozvánkový kód byl úspěšně vygenerován.", "success")
        except Exception as e:
            flash(f"Nepodařilo se vygenerovat kód: {str(e)}", "danger")
    elif form.validate_on_submit():
        req = UpdateCredentialsDTO(old_password=form.old_password.data)
        if form.new_username.data:
            req.new_username = form.new_username.data

        if form.new_password.data:
            req.new_password = form.new_password.data

        token: TokenResponse = services.consumers.update_credentials(req)

        if token:
            resp = redirect(url_for("user.profile"))
            resp = delete_auth_cookie(resp)
            resp = set_auth_cookie(resp, token.access_token)

            return resp
    else:
        if request.method == "POST":
            if invite_form.is_submitted() and not invite_form.validate():
                for field, errors in invite_form.errors.items():
                    for error in errors:
                        flash(str(error), "danger")

            elif form.is_submitted() and not form.validate():
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(str(error), "danger")

    user = services.consumers.get_current_user()
    return render_template("user/profile.html", user=user, form=form, invite_form=invite_form, invite_code=invite_code)

@user.route("/logout", methods=["GET", "POST"])
@authorized
def logout():
    resp = redirect(url_for("auth.index"))
    resp = delete_auth_cookie(resp)
    return resp