from lettuce import step, world
from terrain import SERVER, tidy

E = AssertionError

@step('I connect to +(.*?) *$')
def i_connect_to(step, path):
    world.req = world.www.open(SERVER+path)

@step("I'm logged[ -]?in as +(.*?) *$")
def i_m_logged_in(step, name):
    if ':' in name:
        login, password = name.split(':',1)
    else:
        login, password = name, name

    step.behave_as("""
    Given I connect to /login
    Then I expect HTML
    When I select login_form form
    When I set login_name = %(login)s
    When I set login_password = %(passwd)s
    When I submit
    Then I expect HTML
    """.format({'login': login, 'passwd': password}))

@step('I select +(.*?) +form$')
def i_select_xxx_form(step, name):
    world.req = world.www.select_form(name=name)

@step('I set *(\S+) *= *(\S*) *$')
def i_set_a_is_b(step, name, value):
    world.www[name] = value

@step('I submit')
def i_submit(step):
    world.req = world.www.submit()

@step('I expect HTML')
def i_expect_html(step):
    if not world.www.viewing_html():
        raise E('Not viewing HTML on %r'%world.req.get_url())
    tidy(world.req)

@step('I click on *(.*?) *$')
def i_click_on(step, link):
    world.req = world.www.follow_link(text_regex=link)
