# Transcript: Monroe St NE 8

> **Status:** Historical Record. This document preserves evidence from the date it was written. Do not use it as the current work queue. Current product truth: `docs/00-product-northstar.md`; current state: `STATUS.md`; current rebuild execution: `docs/08-agentic-buildout-plan.md` and `docs/09-rebuild-phase-gates.md`.


- Source audio: `/Users/mschwar/Downloads/Monroe St NE 8.m4a`
- Duration: 00:21:26
- Speakers: Lee Biby, Matt Schwartz, Thomas Gentry
- Generated: 2026-05-06
- Method: OpenAI diarized transcription with short known-speaker reference clips from the prior Monroe St NE recording.
- Note: This is an AI-generated transcript. Review against the audio before quoting exact wording.

## Transcript

**[00:00:18] Matt Schwartz:** yo yo

**[00:00:19] Lee Biby:** Let's get together.

**[00:00:21] Thomas Gentry:** The band together. Fucking nice. What's up, Maggie?

**[00:00:24] Matt Schwartz:** what's up how you doing good

**[00:00:26] Thomas Gentry:** Good, dude. How's the day?

**[00:00:28] Matt Schwartz:** good good how's the pool are

**[00:00:32] Thomas Gentry:** It's nice, bro. I'm in Arizona.

**[00:00:34] Matt Schwartz:** you

**[00:00:35] Thomas Gentry:** Got to get out of the umbrella.

**[00:00:36] Matt Schwartz:** are you in cali are you still are you back in vegas dude

**[00:00:43] Matt Schwartz:** nice is that travel uh fun or is it exhausting

**[00:00:53] Matt Schwartz:** Dude, that's awesome.

**[00:00:55] Thomas Gentry:** Yeah, bro. Big question. I wanted to make sure we're all on the same page. Do you want to give the rundown so it comes from you and it makes sense that we're all on the same page and we each talk to you individually? You know what I mean?

**[00:02:30] Matt Schwartz:** Yep.

**[00:02:31] Thomas Gentry:** And okay, my only variation of that was that instead of us giving complete no guardrails, the only guardrails that we did put is we gave it the amount of queries they could run to being 10 and the max amount of data that they could get would be 100 lines and 100 leads per query. So a total of 1,000 data points. a sandbox environment and we can even use that for a demo now if you want to give us like full access to really see what the tool can do and give us a version that has no parameters fantastic i don't know how hard that is to have like a sandbox environment that we give customers access to you know what i mean and then my other question for you and this might be a future state if we sell it to scotty and we sell it to my business is there any exchange of data There's two big issues that we need to be worried about.

**[00:03:27] Matt Schwartz:** All right.

**[00:03:29] Matt Schwartz:** As of right now, no, but that's something that we can answer more concretely as we build out the product.

**[00:03:43] Thomas Gentry:** But it's possible in some capacity that like Shadow Dragon could somehow get connected. through our tool to one of our other customers right because i'm viewing it like it's a database on the back end where all of this stuff is being we would just have to make sure that there wasn't a bidirectional door between clients or whatever you know

**[00:04:04] Matt Schwartz:** Yeah, yeah. I mean, there wouldn't be lateral connections between clients, right? So the bidirectional door is in and out.

**[00:04:16] Matt Schwartz:** But yeah,

**[00:04:17] Thomas Gentry:** Okay,

**[00:04:17] Matt Schwartz:** so the, no,

**[00:04:17] Thomas Gentry:** it wouldn't be lateral. That's a better way to put it. Yeah, I agree. Okay. So those problems are solved. That'd be my only modification. I'm agreement with everything in summary, the only throttle being the amount of queries being 10 and then the data prompts or whatever the right word is for it, right? The data output being like 100 and maximum. So they got a total of 1,000.

**[00:04:41] Thomas Gentry:** We can use that for demo purposes. Go ahead.

**[00:04:45] Lee Biby:** as a trial run, but the subscription itself that you put in, like, what is that? What do we think that is?

**[00:04:54] Thomas Gentry:** If we sell it, this is where I would think the parameters need to actually come in. Is that same model of, you know, queries to data range, like what's the monetization or cost on that? So we can have a price to the customer versus what we're getting now. and then the other side of it is would there be a way for you to box it in in a capacity where they would have to say something of like give me a job title and a vertical like give me at least two data sets because what i don't want to do is giving them an authentic ai tool and they're like how do we reformulate our supply line right and it's being used as jarvis and it's like i want it to literally just be a lead tool

**[00:05:36] Matt Schwartz:** Yep. um yeah so what are the what are the parameters that would be you would want to hard code in there so like job title vertical um

**[00:05:47] Thomas Gentry:** I would just say that I would want it to be that like I wouldn't want them to be able to go put in any kind of prompt right something that had nothing to do with Legion it would just need to be generic enough where the capability of the system was looking for a lead list right

**[00:06:03] Matt Schwartz:** Yeah.

**[00:06:03] Thomas Gentry:** You know, like, by example, the Lee a minute ago where somebody was talking to Amazon's AI bot and he put in a series of prompts and it got it to do something that it was completely not like supposed to do.

**[00:06:15] Matt Schwartz:** Okay.

**[00:06:16] Thomas Gentry:** It's fine. But do you see what I'm saying? That we want it to be that they go in there and they have to type. We use it freely, but we don't want it to say write it something that it's going to make the tool do something that it doesn't do.

**[00:06:28] Matt Schwartz:** Yeah.

**[00:06:29] Thomas Gentry:** Yeah.

**[00:06:31] Matt Schwartz:** Awesome.

**[00:06:32] Thomas Gentry:** where you could kick back a message that would say hey like please input a vertical or a job title like if it was the output from the tool if they put in something crazy would say you know white rabbit doesn't have that functionality please put in a vertical and job title to search for your next lead list you know

**[00:06:53] Matt Schwartz:** Awesome.

**[00:06:58] Thomas Gentry:** Do we agree with that? Because that's what I think the throttle needs to be. On the amount that they do and when they know how to monetize it, and the throttle needs to be on how many queries they run in the PLC environment and how much data they can pull back, right? And full throttle, we can have it for five days. The UI can stay the way that it is for now. Obviously, we can do some work on it. But, I mean, I don't know what the level of effort is on those throttles. It's not. And I'm not trying to come to you with like a freaking mountain lead. Does that make sense? Matt, does that make sense?

**[00:07:30] Matt Schwartz:** Uh, Lee, you can go first.

**[00:07:34] Thomas Gentry:** Well, I think, yeah, otherwise we're just signing them up for.

**[00:08:56] Thomas Gentry:** You know, I could select if I wanted to give me a CVS file and an Excel file. I can select whatever file output I wanted so that I could upload it into my tool to do the outreach off of.

**[00:09:09] Matt Schwartz:** Correct, yeah.

**[00:09:11] Thomas Gentry:** OK, so that's right. And then also within the file, it tells you how it's been validated, like to check the website against the email. Like I saw something like that as one of the columns. in the file as well as the export that

**[00:09:24] Matt Schwartz:** Yeah.

**[00:09:25] Thomas Gentry:** right as well okay

**[00:09:26] Matt Schwartz:** Yep.

**[00:09:26] Thomas Gentry:** so then to your point me i agree with you completely it's matt if you're comfortable with us being able to scale back its functionality to no matter what fucking prompts that they put in and tells them hey you know it gives them some kind of messaging back saying look enter a prompt along the line of you know job title you digital vertical industry something give them some like suggestions i guess as a consumer and send them back into the tool to crunch it that way because we don't want the tool to be used as just some authentic ai supercomputer and then two we need to figure out what ten thousand dollars right so if they're spending ten thousand dollars on us i would be okay if we were spending a hundred thousand dollars on whatever our cost was as far as the package what are your thoughts about that me did i sum that up am i on the same page

**[00:10:58] Matt Schwartz:** So, this is awesome. This is kind of, it's very clear. You guys are making it really clear, which is great. So, one is we're going to put guardrails on. And right now what we're going to start with is 100 lines per query and the max of 10 queries. That's number one. And number two is we're going to put guardrails on so no matter what the input, the output is going to be limited to lead generation output. That's awesome and done. Like I will do that. In terms of... agreement, not agreement, the way I look at this is I'm 100% on board. This is wonderful. We do it. and then we see what happens do you know what i mean so it's not like it's not like a three-way sign off we're like this is what we're gonna do forever it's more this is a perfect way to start and then yeah like this might be exactly the winning formula it might not but this is freaking awesome this is how this is how things get built right so exactly

**[00:12:12] Lee Biby:** Yeah, no, I agree completely. It's just, I just think that, yeah, it should change. It should more, but we have to start somewhere.

**[00:12:19] Matt Schwartz:** yeah

**[00:12:19] Lee Biby:** We don't. So

**[00:12:21] Matt Schwartz:** This

**[00:12:21] Lee Biby:** this is

**[00:12:21] Matt Schwartz:** is perfect.

**[00:12:22] Lee Biby:** like technically the first tool we're calling it cool If it the same tool wants to do something else cool, but I can't I don't want Thomas to be like Like he's kind of I don't know if he's pulling a favor on this lead for the 10 grand, but it's like we also don't want to

**[00:12:38] Matt Schwartz:** Yeah. Burn

**[00:12:39] Lee Biby:** We

**[00:12:40] Matt Schwartz:** that.

**[00:12:40] Lee Biby:** have money ready to go. It's gonna make sense

**[00:12:42] Thomas Gentry:** I'm capping the makeover for sure, like he's getting the seat at the table for sure, like I've worked. You know what I mean?

**[00:12:48] Matt Schwartz:** So what we're going to do, what I'm going to do is I'm going to get that tool into both of your hands and I'm going to put the guardrails on you for the 10 queries and 100 lines per query. And then I'll give you guys access to it and then you guys can see how it works and we can use that as the starting point.

**[00:13:09] Thomas Gentry:** Bro, and I'm serious. If it works like that, Matt, and I know how to use it. talk about in life you can be out there about your life and i'm telling you conversationally Dude, it's

**[00:13:20] Matt Schwartz:** yeah.

**[00:13:20] Thomas Gentry:** just like a circle because i've been in sales for so long that like it i know a gazillion people that if it's fucking easy and it works well they'll be like yeah we'll super do it because zoom info and uh discover org and those other tools that are lead generation it's like fucking myspace bro you have to fill out so much information there's so much customization and work that goes into like building your list The versatility of just typing in, I want to talk to contractors in Illinois and it gives you fucking a thousand way different, bro.

**[00:13:49] Matt Schwartz:** bro it's it's

**[00:13:50] Thomas Gentry:** So much easier.

**[00:13:51] Matt Schwartz:** win win win win because not only like even if you didn't have the network just by you using it in your daily life for your use case you take the product from being like you know something that's decent and you really give it life right we can make it amazing just based on you and Lee using it um so yeah no it's great that's so the goal is going to be you know by the end of the week

**[00:14:17] Thomas Gentry:** Can I ask you a question,

**[00:14:18] Matt Schwartz:** yeah

**[00:14:18] Thomas Gentry:** just hypothetically? So I get the concept of how to use it in a B2B sense, right? If I want to look for a guy that works this and, and this and whatever, that data makes sense. Now, if I think, forgive me, I forget what it's called, but it's business to consumer, B2C, is that what it's called?

**[00:14:36] Matt Schwartz:** D to C yeah direct to consumer yeah

**[00:14:40] Thomas Gentry:** Yeah. Okay. So if we were running a list to people, right? Like if we wanted to use it for a current job, would you be able to say like, hey, I want a list of everybody that did a refinance on their house in Corrales in the last six months? Like, is that a realistic? Am I thinking about the tool the right way one and is that realistic too?

**[00:15:02] Matt Schwartz:** Okay, so you are thinking about the tool in the right way, and it is realistic. I think for the, let's think of them in terms of like work sprints. I think for the first work, first work sprint I see is getting everything ready for the demo, right, for Scotty.

**[00:15:22] Lee Biby:** Sure.

**[00:15:22] Matt Schwartz:** And then there's going to be another pre-work sprint, which is getting things ready for you guys. And that's what I'm going to be working on right now. So making sure it's ready for you guys helps us get closer to being 100% ready for that demo.

**[00:15:36] Matt Schwartz:** Now, I think it's helpful right now to just focus on B2B because it helps clarify it.

**[00:15:46] Matt Schwartz:** one of the reasons it's really good for we to be using it is because we using it is also going to help us figure out the answer to that question right because i i don't know um but

**[00:15:56] Thomas Gentry:** Right.

**[00:15:59] Thomas Gentry:** technically not right me and I were trying to skip on the other night and I was like imagine if Airbnb wanted to do a scrape of everybody on social media platforms that was open right you didn't have a closed profile but said hey I want you to pull back anybody that's posted pictures in a exotic location in the last 30 days and send me the email that's associated to that Facebook And then, you know, Airbnb can send out an email campaign to all these people saying, hey, you know, we have deals on sale in wherever.

**[00:16:29] Matt Schwartz:** Yep.

**[00:16:29] Thomas Gentry:** Like that would be a viable way for a B2C thing to work. And OK,

**[00:16:33] Matt Schwartz:** Yep.

**[00:16:33] Thomas Gentry:** so that would be phase two. I'm cool with it.

**[00:16:36] Matt Schwartz:** Yep.

**[00:16:36] Thomas Gentry:** Wonderful, man.

**[00:16:37] Matt Schwartz:** Sick, bro. I'm stoked. Yeah.

**[00:16:40] Thomas Gentry:** I

**[00:16:41] Matt Schwartz:** So the

**[00:16:41] Thomas Gentry:** got it.

**[00:16:41] Matt Schwartz:** goal would be by the end of the week, it's the end of the day on Friday, I'll have the tool in your hands and you guys should be able to run your 10 queries. Ideally, you get, you know, a decent amount of lines per query and you're going to be hard capped at a thousand.

**[00:16:57] Thomas Gentry:** That's fucking cool. That's fucking cool. And then do me a favor, right? If I need a reset button. Right where I can do my thousand again because I ran through my 10 I see I see us going through quite a few in the beginning like that's

**[00:17:12] Matt Schwartz:** yeah

**[00:17:12] Thomas Gentry:** the yeah great deal

**[00:17:13] Matt Schwartz:** 100

**[00:17:13] Thomas Gentry:** of the environment for us to have Because being

**[00:17:15] Matt Schwartz:** yeah

**[00:17:16] Thomas Gentry:** able to either text you or however we get the reset button either

**[00:17:19] Matt Schwartz:** the hard the hard cap is one just so you kind of see what it feels like being the customer and two it helps us on the back end like really nail out those kinks and then three yeah of course like you do you you have unlimited essentially um well

**[00:17:35] Thomas Gentry:** And then what is the, how do we figure out the cost, our cost on it? That's,

**[00:17:39] Matt Schwartz:** that's

**[00:17:39] Thomas Gentry:** you know?

**[00:17:39] Matt Schwartz:** here's the thing i can spend a lot of time trying to figure it out right now or we can just let her rip on the first thousand and then see it's not going to be crazy right um

**[00:17:51] Thomas Gentry:** Yeah, okay.

**[00:17:52] Matt Schwartz:** but we'll know we'll know what the answer is right yep

**[00:17:56] Thomas Gentry:** Yeah, we should run four separate thousand ones and check

**[00:18:00] Matt Schwartz:** exactly

**[00:18:00] Thomas Gentry:** to see if it comes back as the same amount.

**[00:18:01] Matt Schwartz:** yeah so so the more we run the more we know so sweet

**[00:18:08] Thomas Gentry:** All right, so we have a plan. Let us know when you have it. I think these little hollows once a week are good, dude.

**[00:18:13] Matt Schwartz:** yeah yeah yeah um

**[00:18:14] Thomas Gentry:** Removing the ball, you know?

**[00:18:15] Matt Schwartz:** and so i i work a ton with ai so i'll be if i ever give you guys info dumps feel free to like my feelings aren't gonna get hurt you're gonna be like too many words say less words or next time send it this way this way this way like just kind of don't think of it as talking to me like this is talking to me but anytime i'm like dumping information usually it's it's being filtered heavily through ai right so just think of it as like info extraction so you can get rid of the niceties just be like yo i need this i need this i need that

**[00:18:52] Thomas Gentry:** Honestly, I think this little tweet and getting it in our hands is going to make us so dangerous. Not going to be able to just interview and be like, how is your DJ this morning? Oh, it's not going to be cool. You have some seconds.

**[00:19:05] Matt Schwartz:** Sweet man. Well, let's talk cool.

**[00:19:08] Thomas Gentry:** Let's do it. All right, boys. I'll let you talk to your team.

**[00:19:12] Matt Schwartz:** All right.

**[00:19:12] Thomas Gentry:** Go ahead, man. If we're talking out our ass, let us talk to you.

**[00:19:16] Matt Schwartz:** No, no, no. I like I will

**[00:19:18] Thomas Gentry:** La la land. It's done.

**[00:19:19] Matt Schwartz:** Well, I like no I 100% will But all this stuff is is like I like I said, it's win-win, you know Like it gives us it makes it easy for me to build because it's so clear and then the signal is gonna be really high whatever we whatever it is the signal is gonna be high, you know, so sweet

**[00:19:38] Thomas Gentry:** They're dangerous, dude. I'm so excited. Oh my God.

**[00:19:42] Matt Schwartz:** All right guys

**[00:19:52] Thomas Gentry:** your money right some

**[00:19:54] Lee Biby:** Oh,

**[00:19:54] Thomas Gentry:** kind

**[00:19:54] Lee Biby:** right.

**[00:19:54] Thomas Gentry:** of sort of sales whatever right some things and then whether they want to send us a check we could take checks and shit like that a lot of time they're like we want to set up an ACH or you know what I mean yep okay by credit card so anyway we just put that food for thought oh

**[00:20:11] Matt Schwartz:** yeah i think whatever whatever we end up doing like whatever lee ends up going with in terms of banking

**[00:20:16] Thomas Gentry:** man I've also calling guys

**[00:20:17] Lee Biby:** Because

**[00:20:17] Matt Schwartz:** okay

**[00:20:17] Lee Biby:** I got to go out

**[00:20:17] Matt Schwartz:** all

**[00:20:17] Lee Biby:** and put

**[00:20:17] Matt Schwartz:** right cool later yeah

**[00:20:20] Lee Biby:** it in the bank account, whatever it's going to be.

**[00:20:22] Matt Schwartz:** whatever you set up that'll be dealt with sweet man sweet sweet well i'm gonna get to freaking staring at a screen dude

**[00:20:31] Lee Biby:** I'm going to keep driving to spend my life. Have a great day.

**[00:20:33] Matt Schwartz:** have fun man all right good luck later
