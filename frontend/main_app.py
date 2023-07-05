import streamlit as st
from streamlit_extras.switch_page_button import switch_page

from frontend import constants, database, utils

# calls only default(login) page
utils.clear_all_but_first_page()

# session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

st.markdown(
    "<h2 style='text-align: center; color: #C059C0;'> Welcome!</h2>",
    unsafe_allow_html=True,
)
st.write("-----")


# Main function
def main():
    # """Login page"""
    menu = ["Login", "SignUp"]
    choice = st.selectbox(
        "Select one option ▾",
        menu,
    )
    # Default choice
    if choice == "":
        st.subheader("Login")
    # if choice login
    elif choice == "Login":
        st.write("-------")
        # st.subheader("Log in")
        with st.form("Login"):
            email = st.text_input("Email Id", placeholder="email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                # if password == '12345':
                # Hash password creation and store in a table
                database.create_usertable()
                hashed_pswd = database.make_hashes(password)
                result = database.login_user(
                    email, database.check_hashes(password, hashed_pswd)
                )

                if result:
                    st.session_state["logged_in"] = True
                    st.success("Logged In Sucessfully")
                else:
                    st.warning("Incorrect Email Id/Password")

    elif choice == "SignUp":
        st.write("-----")
        st.subheader("Create New Account")
        with st.form("Create New Account"):
            new_user = st.text_input("Username", placeholder="name")
            new_user_email = st.text_input("Email id", placeholder="email")
            new_password = st.text_input("Password", type="password")
            signup_button = st.form_submit_button("SignUp")

            if signup_button:

                if new_user == "":  # if user name empty then show the warnings
                    st.warning("Inavlid user name")
                elif new_user_email == "":  # if email empty then show the warnings
                    st.warning("Invalid email id")
                elif new_password == "":  # if password empty then show the warnings
                    st.warning("Invalid password")
                else:
                    database.create_usertable()
                    database.add_userdata(
                        new_user, new_user_email, database.make_hashes(new_password)
                    )
                    st.success("You have successfully created a valid Account!")
                    st.info("Go up and Login to you account.")
    # session state checking
    if st.session_state["logged_in"]:
        utils.show_all_pages()  # call all page
        utils.hide_page(constants.DEFAULT_PAGE.replace(".py", ""))  # hide first page
        switch_page(constants.SECOND_PAGE_NAME)  # switch to second page
    else:
        utils.clear_all_but_first_page()  # clear all page but show first page


if __name__ == "__main__":
    main()
