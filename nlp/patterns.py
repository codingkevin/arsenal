import re

# based on:
#   http://immike.net/blog/2007/04/06/5-regular-expressions-every-web-programmer-should-know/
URL_RE = re.compile("""
(
  # Match the leading part (proto://hostname, or just hostname)
  (
    # http://, https:// or ftp leading part
    (file|ftp|https?)://[-\\w]+(\\.\\w[-\\w]*)+
  |
    # or, try to find a hostname with more specific sub-expression
    (?: [a-z0-9] (?:[-a-z0-9]*[a-z0-9])? \\. )+ # sub domains
    # Now ending .com, etc. For these, require lowercase
    (?: com\\b
        | edu\\b
        | biz\\b
        | gov\\b
        | int\\b
        | info\\b
        | mil\\b
        | net\\b
        | org\\b
        | [a-z][a-z]\\.[a-z][a-z]\\b # two-letter country code
    )
  )

  # Allow an optional port number
  ( : \\d+ )?

  # The rest of the URL is optional, and begins with /
  (
    /
    # The rest are heuristics for what seems to work well
    [^.!,?;"\\'<>()\[\]\{\}\s\x7F-\\xFF]*
    (
      [.!,?]+ [^.!,?;"\\'<>()\\[\\]\{\\}\s\\x7F-\\xFF]+
    )*
  )?
)
""", re.VERBOSE|re.IGNORECASE)


###
# Email validation patterns borrowed from:
#   http://www.regular-expressions.info/email.html

# very very general, probably too general.
RFC2822_RE = re.compile("""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""", re.IGNORECASE)

# removing obsolete bracket notation
# EMAIL_I = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", re.IGNORECASE)


# TODO: add restrictions on email length
#   {local}@{domain}: local 64 characters, domain 255

# refinment of EMAIL-I, it limits country code to 2 letters
EMAIL_RE = re.compile("""
(mailto://)?

[a-z0-9\{\(]                   # startswith alphanum or { or (

[\.a-z0-9\-_/|,]+

[\}\)]?                        # can end with } or )

@                              # crucial!

(?:[a-z0-9]                    # startswith alphanum
   (?:[a-z0-9-]*[a-z0-9])?     # endswith alphanum
   \.                          # the dot in dot com
)+

# the ending .com part
(?:
   com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|edu|[A-Z]{2}
)
""", re.IGNORECASE|re.VERBOSE)

# This pattern is more for validation
EMAIL_STRICT = re.compile('[A-Z0-9._%+-]+@[A-Z0-9.-]+\.(?:com|edu|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|[A-Z]{2})', re.IGNORECASE)


DATE_RE = re.compile("""
(
    # optional: day of the week
    (?:
        (?:mon
            |tues?
            |wed(?:nes)?
            |thurs?
            |fri
            |satu?r?
            |sun
        )(?:day|\.?)

        \s* ,? \s*?

    )?

    \s*
    (?:
        \\b
        (?:\\bthe\\b)?
        \s*
        [0-3]?[0-9]
        \s*
        (?:st|nd|rd|th|)
        \s*
        (?: of )?
        \\b
    )?
    \s*

    # mandatory: month (written)

    \\b(?:jan(?:uary)?
        |febr?(?:uary)?
        |mar(?:ch)?
        |apr(?:il)?
        |may
        |june?
        |july?
        |aug(?:ust)?
        |sept?(?:ember)?
        |oct(?:ober)?
        |nov(?:ember)?
        |dec(?:ember)?
    )\\b[\s.,]*

    (?: [0-3][0-9] | [0-9] )?  (?:(?:st|nd|rd|th|)\\b)?   # the word splitter will always keep numbers ord-suffix together

    \s*  (?: of | , | ) \s*

    (?:  [0-9][0-9][0-9][0-9] | [0-9][0-9] )? \\b

)
""", re.VERBOSE|re.IGNORECASE)


if __name__ == '__main__':

    def test_sentence(x, target=''):
        print
        print 'input: ', x
        output = DATE_RE.findall(x)[0]
        print 'output:', output
        print 'target:', target
        if target:
            assert target.strip() == output.strip()

    test_sentence('I was born on Monday, March of 1986.',  'Monday, March of 1986')
    test_sentence('I was born on Monday, March 18, 1986.', 'Monday, March 18, 1986')
    test_sentence('I was born on March 18 1986 .',         'March 18 1986')
    test_sentence('I was born on Mon. March 18, 86 .',     'Mon. March 18, 86')
    test_sentence('I was born on Mon. March 1, 86 .',      'Mon. March 1, 86')
    test_sentence('I was born on March 18, 86 .',          'March 18, 86')
    test_sentence('I was born on March, 86 .',             'March, 86')
    test_sentence('I was born on March 86 .',              'March 86')
    test_sentence('I was born on Mon. March, 1986 .',      'Mon. March, 1986')
    test_sentence('11th February 1990 , ',                 '11th February 1990')
    test_sentence('the 11th of February , 1990 , ',        'the 11th of February , 1990')
    test_sentence('February, 1990 , ',                     'February, 1990')
    test_sentence('Monday the 3rd of February, 1990 , ',   'Monday the 3rd of February, 1990')
    test_sentence('Mon. the 3rd of February, 1990 , ',     'Mon. the 3rd of February, 1990')
    test_sentence('Mon. 3rd of February, 1990 , ',         'Mon. 3rd of February, 1990')
    test_sentence('Mon. 30th of February 1990 ',           'Mon. 30th of February 1990')
    test_sentence('th February 1990 , ',                   'February 1990')
