This Trust Domain enables data exchange mediated by the pilgrim, on the basis of the pilgrim's consent. The consents are recorded in the [IPS.HAJJ.CONSENT CodeSystem](CodeSystem-IPS.HAJJ.CONSENT.html), and each [Hajj consent](StructureDefinition-HajjConsent.html) in a pilgrim's IPS names one of them in `Consent.policyRule`.

#### Terms of use

The [IPS.HAJJ.CONSENT ValueSet](ValueSet-IPS.HAJJ.CONSENT.html) is this Trust Domain's terms of use: the policies a participant may say it acts under. It is recorded on the [IPS-PILGRIMAGE Trust Domain](http://smart.who.int/trust/Binary-TrustDomain-IPS-PILGRIMAGE.html) in the GDHCN Trust IG. The GDHCN Administrative and Operational Framework 1.2 has no annex for this Trust Domain yet, so that record is drafted from this IG.

#### Naming the consent a VHL Receiver acts under

Under the Verifiable Credential Option of IHE ITI VHL (ITI-YY5), a VHL Receiver retrieves the manifest with a credential it issues itself. It can name the consent policy it acts under in that credential's W3C VC 2.0 `termsOfUse`, with one [Trust Domain policy](http://smart.who.int/trust/StructureDefinition-TrustDomainPolicy.html) entry per policy:

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2"],
  "type": ["VerifiableCredential", "VHLManifestCredential"],
  "issuer": "did:web:vhl-receiver.example.org",
  "validFrom": "2026-06-01T10:00:00Z",
  "validUntil": "2026-06-01T10:05:00Z",
  "credentialSubject": {
    "id": "https://vhl-sharer.example.org/List?_id=abc123def456",
    "manifest": { "url": "https://vhl-sharer.example.org/List?_id=abc123def456", "flag": "LP" },
    "recipient": "Ministry of Health, Saudi Arabia: Haj District facility"
  },
  "termsOfUse": [{
    "type": "http://smart.who.int/trust/StructureDefinition/TrustDomainPolicy",
    "id": "http://smart.who.int/ips-pilgrimage/CodeSystem/IPS.HAJJ.CONSENT#CONSENT-KSA"
  }],
  "proof": { "type": "DataIntegrityProof", "cryptosuite": "ecdsa-rdfc-2019", "proofPurpose": "assertionMethod", "verificationMethod": "did:web:vhl-receiver.example.org#key-1", "proofValue": "z…" }
}
```

The VHL Sharer then:

1. checks that each named policy is in this ValueSet;
2. matches it against the `Consent.policyRule` of the pilgrim's Hajj consents (system and code);
3. decides as the [GDHCN Trust Network: Personal Health Wallet](http://smart.who.int/trust-phw/business-processes.html) process I describes.

Naming a policy only narrows the consents that apply, and it never overrides a prohibition. A credential with no `termsOfUse` is decided on all the pilgrim's applicable consents.
