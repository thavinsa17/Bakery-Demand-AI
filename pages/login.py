import streamlit as st

from utils.ui import page_header
from utils.auth import (
    account_exists,
    authenticate_user,
    register_user,
)

st.set_page_config(
    page_title="Sign In | Bakery Demand AI",
    layout="centered",
)

page_header(
    "Bakery Demand AI",
    "Sign in to manage your bakery demand forecasting.",
)

try:
    registered = account_exists()
except Exception as error:
    st.error(f"Could not check registered accounts: {error}")
    st.stop()

if st.session_state.get("logged_in", False):
    st.success(
        f"You're signed in as "
        f"{st.session_state.get('user_name', 'the bakery user')}."
    )
    st.info("Use the sidebar to open your bakery dashboard.")

    if st.button("Log Out", type="secondary"):
        st.session_state["logged_in"] = False
        st.session_state.pop("user_email", None)
        st.session_state.pop("user_name", None)
        st.rerun()

else:
    if not registered:
        st.info(
            "Welcome! Create the first account for this bakery. "
            "After registration, new account creation will be disabled."
        )

        tab_signup, tab_signin = st.tabs(
            ["Create First Account", "Sign In"]
        )

        with tab_signup:
            with st.form("first_account_form"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                password = st.text_input(
                    "Password",
                    type="password",
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                )

                create_account = st.form_submit_button(
                    "Create Account",
                    type="primary",
                    use_container_width=True,
                )

            if create_account:
                if not full_name.strip() or not email.strip():
                    st.error("Please enter your name and email.")
                elif not password or not confirm_password:
                    st.error("Please enter and confirm your password.")
                elif password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    try:
                        register_user(full_name, email, password)
                        st.success(
                            "Your account has been created. "
                            "Please sign in using your new credentials."
                        )
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))
                    except Exception as error:
                        st.error(f"Could not create account: {error}")

        with tab_signin:
            with st.form("signin_form"):
                email = st.text_input(
                    "Email Address",
                    key="initial_signin_email",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="initial_signin_password",
                )

                signin = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True,
                )

            if signin:
                user = authenticate_user(email, password)

                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = user["email"]
                    st.session_state["user_name"] = user["full_name"]
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    else:
        st.success("Your bakery account is already registered.")

        with st.form("signin_existing_form"):
            email = st.text_input("Email Address")
            password = st.text_input(
                "Password",
                type="password",
            )

            signin = st.form_submit_button(
                "Sign In",
                type="primary",
                use_container_width=True,
            )

        if signin:
            user = authenticate_user(email, password)

            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["user_name"] = user["full_name"]
                st.rerun()
            else:
                st.error("Invalid email or password.")