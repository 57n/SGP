# Learning Synchronous Grammar Patterns for Assisted Writing for Second Language Learners

論文刊登於2017 IJCNLP System Demo

Wu, Chi-En, et al. "Learning Synchronous Grammar Patterns for Assisted Writing for Second Language Learners." Proceedings of the IJCNLP 2017, System Demonstrations (2017): 53-56.
http://www.aclweb.org/anthology/I17-3014

System demo link:
https://spg-write.herokuapp.com/

Step1. 處理英文資料

	i. 將英文語料做tokenization
	$ cat ltn_news.en.clean | python3 word_token.py > ltn_news.en.token

	ii. 將 tokennize 過後的英文語料做 Truecasing ，以減少 sparsity ， truecase.perl 程式放在 recaser 資料夾底下
	note: truecaser-bnc.model 是用 warehouse 上 bnc 的資料產生的 model ，如何產生 truecaser model 參見：http://jon.dehdari.org/teaching/uds/smt_intro/
	$ perl truecase.perl --model truecaser-bnc.model <ltn_news.en.token> ltn_news.en.truecase

	iii. 將做完 Truecasing 後的英文語料用 geniatagger 來做 tagging
	note: geniatagger 在 ironman 上已安裝
	$ cat ltn_news.en.truecase | ./geniatagger > ltn_news.en.genia

	iv. 將產生出來的genia格式轉檔成每行一句子的格式
	$ cat ltn_news.en.genia | python3 genia_transformat.py > ltn_news.en.tag

Step2. 處理中文資料
	
	note: 中文斷詞程式在ckip資料夾底下，該程式在linux環境下才能執行，建議放在ironman上跑
	PyWordSeg.py 在 ckip/wordseg/WordSeg/lib 資料夾底下

	i. 將中文語料做斷詞
	$ ./lib/PyWordSeg.py ini/ws_uw.ini ltn_news.ch.clean ltn_news.ch.tag

Step3. 合併語料庫
	
	i. 將上述處理完畢的中英語料做合併
	$ cat FBIS.en.tag ltn_news.en.tag TED.en.tag UM-Corpus.en.tag > MIXED-Corpus.en.tag
	$ cat FBIS.ch.tag ltn_news.ch.tag TED.ch.tag UM-Corpus.ch.tag > MIXED-Corpus.ch.tag

	ii. 將合併完成的語料轉換成 fast_align格式
	$ python3 to_fast_align_format.py MIXED-Corpus.en.tag MIXED-Corpus.ch.tag MIXED-Corpus.fast_align

Step4. 將合併後的平行語做 sentence align
	
	note: fast_align安裝及使用參考以下網址：
	https://github.com/clab/fast_align

	i. 執行 fast_align
	$ ./fast_align -i MIXED-Corpus.fast_align  -d -o -v > forward.align
	$ ./fast_align -i MIXED-Corpus.fast_align  -d -o -v -r > reverse.align
	$ ./atools -i forward.align -j reverse.align -c grow-diag-final-and > MIXED-Corpus.align

Step5. 取得最終可用資料以及產生結果
	
	i. 將所有資訊合併，輸出後檔案的格式為 ： 斷詞後的英文 ||| 斷詞後的中文 ||| 中英 alignment ||| 英文 lemma ||| 英文 POS tags |||  英文 BIO 格式 chunk tags ||| 中文 POS tags
	$ python3 combine_all_info.py MIXED-Corpus.en.tag MIXED-Corpus.ch.tag MIXED-Corpus.align MIXED-Corpus.all
    
    ii. 用 grep 指令將含有目標動詞的句子抓出來（參見grep_verbs.sh）（也可跳過這步驟，但往後查詢會比較慢）
    $ cat MIXED-Corpus.all | grep "consider " > ./Verbs/consider.txt
	$ cat MIXED-Corpus.all | grep "apologize " > ./Verbs/apologize.txt
	$ cat MIXED-Corpus.all | grep "run " > ./Verbs/run.txt
	.
	.
	.

	iii. 執行 SPG_gen.py 以產生 SPG （第一個參數為查詢動詞，第二個參數為輸入的pattern，第三個為顯示的例句數量，若不輸入第二個參數則會自動從_collins.pg.v找pattern）
	$ python3 SGP_gen.py save ‘V n from n’ 3
	$ python3 SGP_gen.py apologize
	$ python3 SGP_gen.py run ‘V for n’
	.
	.
	.


其他資料說明：
en_pat.ch_pat.txt 裡放的是對於每個English pattern template中常翻成的 Chinese template  
coll.verbs.txt 裡是從collins抓到的所有動詞

