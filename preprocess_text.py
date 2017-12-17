import re

keywords = 'GOAL!|CLOSE!|PENALTY!|KICK-OFF!|CHANCE!|SUB!|WIDE!|SAVE!|YELLOW!'
remove_words = ['watch','click here']
filenames = ['doc1.txt']
for i in range(1,11):
  filename = '../text_commentaries/doc'+str(i)+'.txt'
  f = open(filename)
  text = f.read()
  text = re.sub(r'[\d]+:[\d]+\n[\w]+ [\d]+-[\d]+ [\w]+','', text)
  text = re.sub(r'[\d]+:[\d]+','', text)
  text = re.sub(r'[\w]+ [\d]+-[\d]+ [\w]+','', text)
  # Split lines based on their comment time not by sentences
  lines = re.split(r"[\d]+: ", text)
  for ind in range(0,len(lines)):
    row = lines[ind]
    words = re.findall(keywords,row.upper())
    if words:
      for w in words:
          row = re.sub(w,w[0:-1]+',', row)
    lines[ind] = row

  lines.reverse()

  lines = ' '.join(lines).split('\n')

  for row in lines:
      if any(word in row.lower() for word in remove_words):
          lines.remove(row)

  filter(None, lines)
  text = ' '.join(lines)
  f.close()
  new_filename = '../processed_text_commentaries/doc'+str(i)+'.txt'
  fo = open(new_filename,'w')
  fo.write(text)
  fo.close()
