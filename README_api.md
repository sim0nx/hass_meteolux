Home Assistant MeteoLux integration.

## Weather Icon Mappings
Reference: https://data.public.lu/en/datasets/meteolux-luxembourg-weather-forecast-for-the-current-day/#/discussions/5b190f8b46f3b561d9a42719

List is only available in French.
Format description:
- Icon number
- J=jour, N=nuit, P=precipitation, F=freezing and snow
- Description

```json
{
    {"00", "JN--", ""},
    {"01", "J---", "Ensoleillé"},
    {"02", "J---", "Ciel voilé"},
    {"03", "J---", "Peu nuageux"},
    {"04", "J---", "Nuageux"},
    {"05", "JN--", "Couvert"},
    {"06", "JN--", ""},
    {"07", "-N--", "Ciel dégagé"},
    {"08", "-N--", "Ciel voilé"},
    {"09", "-N--", "Peu nuageux"},
    {"10", "-N--", "Nuageux"},
    {"11", "JN--", ""},
    {"12", "J---", "Brume"},
    {"13", "-N--", "Brume"},
    {"14", "JN--", "Brouillard"},
    {"15", "JN-F", "Brouillard givrant"},
    {"16", "JN--", ""},
    {"17", "JNP-", "Pluie et bruine faible"},
    {"18", "JNP-", "Bruine faible"},
    {"19", "JNP-", "Bruine modérée"},
    {"20", "JNP-", "Bruine et pluie"},
    {"21", "JNP-", "Pluie faible"},
    {"22", "JNP-", "Pluie modérée"},
    {"23", "JNP-", "Pluie forte"},
    {"24", "JNPF", "Pluie et neige modéré"},
    {"25", "JNPF", "Faibles chutes de neige"},
    {"26", "JNPF", "Chutes de neige modérées"},
    {"27", "JNPF", "Pluie verglaçante"},
    {"28", "J-PF", "Averse de grésil"},
    {"29", "-NPF", "Averse de grésil"},
    {"30", "J-P-", "Faible averse de pluie"},
    {"31", "J-P-", "Averse de pluie modéré"},
    {"32", "J-PF", "Averse de pluie et neige"},
    {"33", "J-PF", "Faible averse de neige"},
    {"34", "J-PF", "Averse de neige modérée"},
    {"35", "J-PF", "Averse de grêle"},
    {"36", "-NP-", "Faible averse de pluie"},
    {"37", "-NP-", "Averse de pluie modéré"},
    {"38", "-NPF", "Averse de pluie et neige"},
    {"39", "-NPF", "Faible averse de neige"},
    {"40", "-NPF", "Averse de neige modérée"},
    {"41", "-NPF", "Averse de grêle"},
    {"42", "JN--", "Orage"},
    {"43", "JNPF", "Pluie et neige faible"},
    {"44", "J-PF", "Pluie et neige faible"},
    {"45", "-NPF", "Pluie et neige faible"},
    {"46", "JN--", ""},
    {"47", "JNPF", "Orage avec grésil"},
    {"48", "JNP-", "Orage avec pluie faible"},
    {"49", "JNP-", "Orage avec pluie modérée"},
    {"50", "JNPF", "Orage avec pluie et neige"},
    {"51", "JNPF", "Orage avec neige faible"},
    {"52", "JNPF", "Orage avec neige modérée"},
    {"53", "JNPF", "Orage avec grêle"},
    {"54", "JN--", "Vent fort"},
    {"55", "JN-H", "Température très haute"},
    {"56", "JN-F", "Température très basse"},
    {"57", "J---", "Orage, soleil visible"},
    {"58", "J-P-", "Orage avec pluie, soleil visible"},
    {"59", "J-PF", "Orage avec neige, soleil visible"}
}
```

Please find below the definition of the updated indexes for warnings (weather phenomena):
- 02: wind
- 03: rain
- 04: snow
- 05: freezing precipitation
- 06: thunderstorm
- 09: heat
- 10: frost
- 11: flooding
- 13: O3
- 14: PM10

The associated color codes for the level of warning are:
- green: no special warning
- yellow: potential danger
- orange: danger
- red: extreme danger
