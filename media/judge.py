import subprocess, sys, random, time

test = []
"""
for i in range(1, 10):
	with open('test_data/letters.in%d' % i) as fp:
		a = fp.read()
	with open('test_data/letters.ou%d' % i) as fp:
		b = fp.read().strip()
	test.append((a, b))

with open('test_data/letters.ina') as fp:
	a = fp.read()
with open('test_data/letters.oua') as fp:
	b = fp.read().strip()
test.append((a, b))
"""

p = subprocess.Popen(['g++', '-O2', '-std=c++1y', 'tcc.cpp', '-o', 'tcc'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
p.communicate()
for i in range(1, 100):
	#t = test[i]
	#p = subprocess.Popen(['python3', 'boj.py'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	a = random.randrange(1, 10000000000000000000)
	b = random.randrange(1, 10000000000000000000)
	p = subprocess.Popen(['python3', 'test.py'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	p.stdin.write(str.encode('%d %d' % (a, b)))
	out, err = p.communicate()
	real_ans = out.decode().strip()
	p = subprocess.Popen(['./tcc'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	p.stdin.write(str.encode('%d %d' % (a, b)))
	start = time.time()
	out, err = p.communicate()
	end = time.time()
	your_ans = out.decode().strip()
	if your_ans != real_ans:
		print('입력: %d %d' % (a, b))
		print('출력: %s' % your_ans)
		print('정답: %s' % real_ans)
	else:
		print('맞았습니다! (%.2fs)' % (end - start))