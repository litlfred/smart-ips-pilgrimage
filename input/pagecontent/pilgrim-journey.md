The [user scenarios](scenarios.html) of this guide told as one pilgrim's story,
step by step along the [overview of key process flows](business-processes.html)
(the numbered steps 1–5 and A–B of the figure below). Each moment names who
takes part, what happens, and what in this guide specifies it, and asks the
policy question it raises. Where the guide does not yet specify a moment, the
moment says so.

<div class="stu-note" markdown="1">
**Every person in this story is fictional.** The setting follows this guide's
[Malaysian reference implementation](reference-implementations-malaysia.html):
a pilgrim from Malaysia performing Hajj in the Kingdom of Saudi Arabia (KSA).
</div>

<img src="workflow.png" alt="Overview of key process flows: steps 1 to 5 between the home country, the pilgrim and KSA, and steps A and B through WHO GDHCN" style="width:70%"/>

### The people

| Person | Who they are | Generic persona |
|---|---|---|
| **Kamal** | 61, from Kuala Terengganu, Malaysia, performing Hajj for the first time. Has type 2 diabetes and high blood pressure; takes insulin and two tablets a day; allergic to penicillin. Carries one phone. | [Pilgrim](personas.html) |
| **Salmah** | Kamal's wife, travelling with him. Speaks for him when he cannot. | Accompanying family member (not yet a persona here) |
| **Dr Aisyah** | General practitioner in Kuala Terengganu, empanelled by the national pilgrimage authority for pre-Hajj health examinations. | [Counsellor](personas.html) |
| **Dr Hafiz** | Doctor of the Malaysian Hajj medical team, travelling with the pilgrims. | [Accompanying Clinician from Origin Country](personas.html) |
| **Nurse Reem** | Registration nurse at a Hajj health facility in Mina. | [Host Country Health Worker](personas.html) |
| **Dr Faisal** | Emergency physician at the same facility. | [Host Country Health Worker](personas.html) |

And the systems: Kamal's **national health wallet** ([Origin Country Wallet](system-actors.html#ochw)),
Malaysia's **health information exchange** ([Origin Country HIE](system-actors.html#ochie)),
the facility's **EMR** ([Host Country EMR](system-actors.html#hcemr)), and **WHO GDHCN**,
the trust network both countries take part in.

### P0 · Before the season — keys and codes are shared (step A)

<img src="pilgrim/p0.webp" alt="A Malaysian government building and a Saudi ministry building far apart; a golden key travels from Malaysia to a blue globe of linked dots between them, and code books to the Saudi side." style="width:100%;max-width:640px"/>

Malaysia's HIE publishes the public keys it signs health documents with to the
WHO GDHCN trust network, and shares the national code systems its IPS uses with
the WHO Terminology Service ([user scenarios](scenarios.html), first two sections).
Nothing about Kamal yet: this is what lets a Saudi clinic trust and read a
Malaysian record months later.

- **Specified by:** the [SMART Trust](https://smart.who.int/trust) framework, by reference.
- **Not yet specified here:** no business process or transaction for publishing keys or terminologies.
- **Policy question:** which Malaysian institution signs health documents on behalf of the health sector, and who in KSA decides to accept that signature?

### P1 · The health check and the choice to share (step 1)

<img src="pilgrim/p1.webp" alt="In a Kuala Terengganu clinic, Dr Aisyah explains a consent card with a shield and a calendar to Kamal, in a batik shirt, who holds his phone with a padlock and a tick; Salmah sits beside him." style="width:100%;max-width:640px"/>

Three months before Hajj, Kamal has the mandatory pre-Hajj health examination
with Dr Aisyah. He is fit to travel. She explains what the Hajj Health Record
is, who can see it, and for how long. Kamal agrees on his wallet to share his
patient summary with Saudi health workers during Hajj, and sets how the link
to it is protected.

- **Specified by:** business processes *Health Check and Counseling, Explicit Consent on Wallet* and *Verbal Consent* ([Business Processes](business-processes.html));
  transaction [record consent from wallet](transactions.html#record-consent-request);
  profile HajjConsent and its examples *CONSENT-MYS* and *CONSENT-KSA* ([Artifacts](artifacts.html)).
- **Not yet specified here:** the two forms the pilgrim fills in, *consent-wallet-questionnaire* and *shl-configure-privacy-settings*, are named in the processes but not defined.
- **Policy question:** is consent given once for the whole Hajj season, per facility, or per encounter — and can Kamal withdraw it while abroad?

### P2 · His summary is assembled and signed (step 2)

<img src="pilgrim/p2.webp" alt="Icons for his conditions, medicines and allergy are gathered into one summary, stamped with a green shield by a golden key and turned into a QR code on the phone Kamal holds beside his packed suitcase." style="width:100%;max-width:640px"/>

Malaysia's HIE assembles Kamal's International Patient Summary from his care
history: his conditions, his medicines, his allergy. It issues a Verifiable
Health Link to it, signs it with a key registered with GDHCN, and puts the QR
code in his wallet.

- **Specified by:** transaction [issue VHL](transactions.html#issue-vhl-request);
  profile HajjIPS and the example *My IPS*; the folder example *My Hajj Pilgrimage Minimal Folder* ([Artifacts](artifacts.html)).
- **Not yet specified here:** no business process for assembling the IPS from the care history.
- **Policy question:** what must the summary contain for a pilgrim — and who decides what is left out?

### P3 · Taken ill in Mina (step 3)

<img src="pilgrim/p3.webp" alt="In the white tents of Mina under a hot sun, Kamal in ihram holds his forehead, dizzy; Salmah supports his arm and Nurse Reem welcomes them at the health facility." style="width:100%;max-width:640px"/>

On the second day in Mina, in the heat, Kamal feels dizzy and weak. Salmah
brings him to the Hajj health facility. At registration he opens his wallet
and shows Nurse Reem the QR code.

- **Specified by:** business process *Clinical Encounter for Unplanned Care* ([Business Processes](business-processes.html)).
- **Policy question:** what should happen when a pilgrim arrives with no phone, a flat battery, or no QR code?

### P4 · Scanned and checked (step 4, step B)

<img src="pilgrim/p4.webp" alt="Nurse Reem scans the QR code on Kamal's phone; the facility screen shows a passcode and a green shield, while a key comes back from the trust-network globe." style="width:100%;max-width:640px"/>

Nurse Reem scans the code in the facility's EMR and enters the passcode. The
EMR checks the signature with Malaysia's public key, fetched from GDHCN: the
record really comes from Malaysia's HIE and has not been changed.

- **Specified by:** the same process (tasks *scan QR code*, *add passcode*, *verify QR code signature*); the receiving steps of the [Malaysian reference implementation](reference-implementations-malaysia.html).
- **Not yet consistent here:** the [concepts](concepts.html) say the default passcode is the pilgrim's birth date; the Malaysian implementation sets one standard passcode for all its pilgrims for the season.
- **Policy question:** what protection should the passcode give — and is a passcode shared by every pilgrim of a country a passcode at all?

### P5 · His record is read and he is treated (step 5)

<img src="pilgrim/p5.webp" alt="Kamal lies recovering on a bed with a drip, Salmah beside him; Dr Faisal shows a tablet with an insulin pen, a crossed-out penicillin capsule and a heart, read from the record kept in Malaysia." style="width:100%;max-width:640px"/>

The EMR follows the link to Malaysia's HIE and retrieves Kamal's summary. Dr
Faisal sees the insulin and the penicillin allergy before he treats him for
heat exhaustion and low blood sugar. The EMR keeps a rendered copy of the
summary with the record of the visit.

- **Specified by:** transactions [retrieve VHL folder](transactions.html#retrieve-VHL-manifest-request) and [retrieve IPS](transactions.html#retrieve-IPS-request); the [Host Country EMR](system-actors.html#hcemr)'s duty to keep a rendered copy; test case *View IPS content* ([Testing](testing.html)).
- **Not yet specified here:** the summary is in the language it was written in; nothing says how a Saudi clinician reads a summary written in Malay.
- **Policy question:** does Malaysia learn that Kamal's record was opened in KSA, and by whom?

### P6 · When he cannot show the code (Phase 2: break the glass)

<img src="pilgrim/p6.webp" alt="At dusk on the plain of Arafat, Kamal lies unconscious on a stretcher; Dr Hafiz of the Malaysian medical team hands Dr Faisal a phone with his registration number, under a broken-glass emergency sign and an open padlock." style="width:100%;max-width:640px"/>

On the day of Arafat Kamal collapses and is brought in unconscious. Salmah is
not with him. Dr Hafiz of the Malaysian medical team gives his Hajj
registration number, and the facility reaches his summary through it.

- **Specified by:** described in [user scenarios](scenarios.html) as a Phase 2 scenario; the [Origin Country Wallet](system-actors.html#ochw) lets the pilgrim opt in or out of break-the-glass access.
- **Not yet specified here:** no business process, transaction or consent profile for emergency access.
- **Policy question:** who may open an unconscious pilgrim's record, on what legal basis, and how is it accounted for afterwards?

### P7 · Back home (after the story the guide tells)

<img src="pilgrim/p7.webp" alt="Back in Kuala Terengganu, Kamal in a white kopiah and Salmah sit with Dr Aisyah, who looks at her computer with a question mark: the record of his care in Saudi Arabia has not come home." style="width:100%;max-width:640px"/>

Kamal comes home. His GP in Kuala Terengganu does not know he was treated in
Mina.

- **Not yet specified here:** nothing returns the record of care in KSA, or a log of who opened his summary, to Malaysia.
- **Policy question:** should the host country send a summary of care back to the home country — and with whose consent?

### What the story shows the guide still needs

1. Business processes for P0 (keys and terminologies), P2 (assembling the IPS) and P6 (break the glass).
2. The two pilgrim forms named in P1, and a page for the pilgrim and counsellor actors: their actor files exist but no page includes them.
3. One passcode policy (P4), stated once.
4. An account of access back to the home country (P5, P7), and of language (P5).
5. Example patients that are pilgrims: today's examples are a resident of the Netherlands.
6. The data dictionary, decision logic, indicators and functional requirements, which are still placeholders.
