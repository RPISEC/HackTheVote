Sanders Fan Club
---

On the main page we find two flag images. The first image, flag1.jpg comes up as a regular image, but if we open flag2.jpg in a new tab we get the raw bytes back instead of the picture being rendered.

If we view the network traffic using the browser's developer console we can see that we actually make two or three requests, which is odd since all we did was request the jpg.

Examining the separate requests we see that for the first our browser requested `Accept: "text/html"` and got our jpg bytes as a response, but with `Content-type` set `text/css`. We now know why we got bytes instead of the image, but why was the response Content-type different?

For the second request our browser set `Accept: "text/css"` and we got actual CSS code back, from the same URL. At the bottom of this CSS we see the message
```
/* 
 * How did I... Nevermind. I'm pretty sure my creds are in a text file
 */
```

Since the our browser set `Accept: "text/html"` and got our jpg bytes, and then it set `Accept: "text/css"` and got CSS, we can infer that setting `Accept: "text/plain"` will get us this text file. It does and the  file contains the flag.
