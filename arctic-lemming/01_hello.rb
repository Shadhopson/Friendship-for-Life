require 'squib'
#unnecessary part
data = Squib.csv file: 'cardData.csv'
layouts = ['economy.yml', '_part2_01_factions.yml']
Squib::Deck.new cards: data['name'].size, layout: layouts  do
    background color: 'white'
    rect layout: 'cut'
    rect layout: 'safe'
    text str: data['name'], layout: 'title'
    text str: data['power'], layout: 'description'
    text str: Time.now, layout: 'credits'
    svg layout: data['faction']
    save_sheet prefix: '_part2_01_factions_', columns: 4
    save_pdf trim: 37.5
end
#children
data = Squib.csv file: 'friendshipCards.csv'

Squib::Deck.new cards: data['Name'].size, layout: layouts do
    background color: 'white'
    rect layout: 'cut'
    rect layout: 'safe'
    text str: data['Name'], layout: 'name'
    text str: 'Skill Boost', layout: 'skill_description'
    text str: data['Skill Boost'], layout:  'skill_boost'
    text str: 'Needs Fulfilled', layout: 'need_description'
    text str: data['Need Fulfilled 1'], layout: 'needs_fulfilled'
    text str: data['Need Fulfilled 2'], layout: 'needs_fulfilled_2'
    svg layout: data['Type']
    save_sheet prefix: 'friendship', columns: 4
    save_pdf dir: "pdfs", file: "kids.pdf", trim: 37.5
end
#jobs
data = Squib.csv file: 'jobCards.csv'

Squib::Deck.new cards: data['Position'].size, layout: layouts do
    background color: 'white'
    rect layout: 'cut'
    rect layout: 'safe'
    text str: data['Position'], layout: 'name'
    text str: 'Necessary Skills', layout: 'skill_description'
    text str: data['Skills Needed 1'], layout: 'skill_boost'
    text str: data['Skills Needed 2'], layout: 'skill_2'
    text str: data['Skills Needed 3'], layout: 'skill_3'
    text str: 'Needs Fulfilled', layout: 'need_description'
    text str: data['Benefit 1'], layout: 'needs_fulfilled'
    text str: data['Benefit 2'], layout: 'needs_fulfilled_2'
    text str: data['Benefit 3'], layout: 'needs_fulfilled_3'
    text str: 'Pay:', layout: 'pay_label'
    text str: data['Pay'], layout: 'pay'
    save_sheet prefix: 'jobs', columns: 4
    save_pdf dir: "pdfs", file: "jobs.pdf", trim: 37.5

end

#partner
#
data = Squib.csv file: 'partnerCards.csv'
Squib::Deck.new cards: data['Finances'].size, layout: layouts do
    background color: 'white'
    rect layout: 'cut'
    rect layout: 'safe'
    text str: data['Name'], layout: 'name'
    text str: 'Their Standards', layout: 'skill_description'
    text str: data['Need 1'], layout: 'skill_boost'
    text str: data['Need 2'], layout: 'skill_2'
    text str: data['Need 3'], layout: 'skill_3'
    text str: 'Needs Fulfilled', layout: 'need_description'
    text str: data['Support 1'], layout: 'needs_fulfilled'
    text str: data['Support 2'], layout: 'needs_fulfilled_2'
    text str: data['Support 3'], layout: 'needs_fulfilled_3'
    text str: data['Support 4'], layout: 'needs_fulfilled_4'
    text str: 'Finances', layout: 'pay_label'
    text str: data['Finances'], layout: 'finances'
    save_sheet prefix: 'partners', columns: 4
    save_pdf dir: "pdfs", file: "partners.pdf", trim: 37.5
end

#hobbies
data = Squib.csv file: 'hobbyCards.csv'
Squib::Deck.new cards: data['Hobby'].size, layout: layouts do
    background color: 'white'
    rect layout: 'cut'
    rect layout: 'safe'
    text str: data['Hobby'], layout: 'name'
    text str: 'Skills Gained', layout: 'skill_description'
    text str: data['Skill Gained 1'], layout: 'skill_boost'
    text str: data['Skill Gained 2'], layout: 'skill_2'
    text str: data['Skill Gained 3'], layout: 'skill_3'
    text str: data['Skill Gained 4'], layout: 'skill_4'
    text str: 'Needs Fulfilled', layout: 'need_description'
    text str: data['Need Fulfilled 1'], layout: 'needs_fulfilled'
    text str: data['Need Fulfilled 2'], layout: 'needs_fulfilled_2'
    text str: data['Need Fulfilled 3'], layout: 'needs_fulfilled_3'
    text str: data['Need Fulfilled 4'], layout: 'needs_fulfilled_4'
    save_sheet prefix: 'hobbies', columns: 4
    save_pdf dir: "pdfs", file: "hobbies.pdf", trim: 37.5
end

