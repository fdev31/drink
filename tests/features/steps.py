from lettuce import step, world
from terrain import tidy
import json

E = AssertionError

@step('I connect to +(.*?) *$')
def i_connect_to(step, path):
    world.req = world.www.get(path)

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

@step("I'm logged[ -]?out *$")
def i_m_logged_out(step):
    step.behave_as("""
    Given I connect to /logout
    Then I expect HTML
    """)

@step('I select +(.*?) +form$')
def i_select_xxx_form(step, name):
    world.form = world.req.forms[name]

@step('I set *(\S+) *= *(\S*) *$')
def i_set_a_is_b(step, name, value):
    world.form[name] = value

@step('I submit')
def i_submit(step):
    world.form.submit()

@step('I expect HTML')
def i_expect_html(step):
    if not world.req.html:
        raise AssertionError('Not HTML!')
    else:
        world.html = world.req.html
    #if not world.www.viewing_html():
        #raise E('Not viewing HTML on %r'%world.req.get_url())
    tidy(world.req.body)

@step(u'I expect empty content')
def i_expect_empty_content(step):
    if world.req.body:
       raise AssertionError('There is content ! :( %r'%world.req.body[:100])

@step('I expect JSON *(.*)$')
def i_expect_json(step, what):
    world.json = json.loads(world.req.body)
    if what:
        if what not in world.json:
            if not (what == 'error' and not world.json):
                raise AssertionError("%r not found in %r"%(what, world.json))

@step('I click on *(.*?) *$')
def i_click_on(step, link):
    world.req = world.req.click(linkid=link)
