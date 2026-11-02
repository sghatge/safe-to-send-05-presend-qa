Safe to Send · Ep 05 — Four defects a tired team ships at 23:00

I ran five Black Friday deliveries through nine pre-send checks. One passed. Four were blocked:

🇸🇮 Slovenia: no unsubscribe link (the preferences link looked close enough at 23:00)
🇦🇹 Austria: no proof sign-off
🇬🇷 Greece: "€1,299.00" instead of "1.299,00 €", and a 23:30 send
🇭🇺 Hungary: no marketing-consent filter, plus a 67-character subject

I've seen every one of these reach a real customer in my career.

None of the nine checks needs AI. They're deterministic, around 100 lines of Python, and each one maps to Adobe's own delivery guidance. What matters is that they run every time, before anyone, human or agent, presses send.

The repo exits with code 1 when anything blocks, so you can drop it into a pipeline today.

Which check would you add?

Repo: https://github.com/sghatge/safe-to-send-05-presend-qa

#SafeToSend #EmailMarketing #AdobeCampaign #QA
